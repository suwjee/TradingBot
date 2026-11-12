import { spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import { createInterface } from "node:readline";

const EXPIRED = "The live indicator session is unavailable. Use Apply again.";

export class LiveEngineError extends Error {
  constructor(status, message, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function startLiveEngineWorker({ command, args, env, onProgress, timeoutMs = 300_000 }) {
  const child = spawn(command, args, { env, windowsHide: true });
  const output = createInterface({ input: child.stdout, crlfDelay: Infinity });
  const errors = createInterface({ input: child.stderr, crlfDelay: Infinity });
  let pending;
  let closed = false;
  let seedProgress = onProgress;

  function settle(error, message) {
    if (!pending) return;
    const { resolve, reject, timer } = pending;
    pending = null;
    clearTimeout(timer);
    if (error) reject(error);
    else resolve(message);
  }

  function close(error = new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED")) {
    if (closed) return;
    closed = true;
    seedProgress = null;
    settle(error);
    output.close();
    errors.close();
    child.kill();
  }

  function receive(type, request) {
    if (closed) return Promise.reject(new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED"));
    if (pending) return Promise.reject(new LiveEngineError(429, "The live indicator is busy."));
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => close(new LiveEngineError(410,
        "The live Engine did not respond. Use Apply again.", "LIVE_ENGINE_TIMEOUT")), timeoutMs);
      timer.unref();
      pending = { type, resolve, reject, timer };
      if (request) {
        child.stdin.write(`${JSON.stringify(request)}\n`, error => {
          if (error) close();
        });
      }
    });
  }

  errors.on("line", line => {
    const prefix = "QG_PROGRESS:";
    if (seedProgress && line.startsWith(prefix)) {
      try { seedProgress(JSON.parse(line.slice(prefix.length))); } catch {}
    }
  });
  output.on("line", line => {
    let message;
    try { message = JSON.parse(line); }
    catch {
      close(new LiveEngineError(410, "The live Engine returned an invalid response.", "LIVE_ENGINE_PROTOCOL"));
      return;
    }
    if (message?.type === "error") {
      if (message.code === "RAW_RETRY") {
        settle(new LiveEngineError(503, message.message, message.code));
        return;
      }
      const status = message.code === "RAW_CHANGED" ? 409 : 410;
      close(new LiveEngineError(status, message.message || EXPIRED, message.code));
      return;
    }
    if (!pending || message?.type !== pending.type || !message.payload?.directions
        || (message.type === "seed" && typeof message.ready !== "boolean")) {
      close(new LiveEngineError(410, "The live Engine returned an unexpected response.", "LIVE_ENGINE_PROTOCOL"));
      return;
    }
    if (message.type === "seed") seedProgress = null;
    settle(null, message);
  });
  child.on("error", () => close());
  child.stdin.on("error", () => close());
  child.on("close", () => close());

  return {
    seed: receive("seed"),
    async update(data, sha256) { return (await receive("update", { data, sha256 })).payload; },
    close,
  };
}

export function createLiveEngineSessions({ maxSessions = 4, idleTtlMs = 30 * 60_000, now = Date.now } = {}) {
  const sessions = new Map();
  let closed = false;

  function discard(id) {
    const session = sessions.get(id);
    if (!session) return;
    sessions.delete(id);
    session.worker.close();
  }

  function expire() {
    for (const [id, session] of sessions) {
      if (!session.seeding && !session.pending && now() - session.touched >= idleTtlMs) discard(id);
    }
  }

  const timer = setInterval(expire, Math.min(idleTtlMs, 60_000));
  timer.unref();

  async function seed({ chartId, sourceFingerprint, request }, launch) {
    if (closed) throw new LiveEngineError(503, "The server is shutting down.");
    expire();
    if (sessions.size >= maxSessions) {
      const oldest = [...sessions].filter(([, session]) => !session.seeding && !session.pending)
        .sort(([, a], [, b]) => a.touched - b.touched)[0];
      if (!oldest) throw new LiveEngineError(429, "All live indicator sessions are busy.");
      discard(oldest[0]);
    }
    const id = randomBytes(16).toString("hex");
    const worker = launch();
    const session = { worker, chartId, sourceFingerprint, request, seeding: true, touched: now(), latest: null };
    sessions.set(id, session);
    try {
      const { payload, ready } = await worker.seed;
      if (!ready) {
        discard(id);
        return { payload, sessionId: null };
      }
      if (closed || sessions.get(id) !== session) throw new LiveEngineError(503, "The server is shutting down.");
      session.seeding = false;
      session.touched = now();
      return { payload, sessionId: id };
    } catch (error) {
      discard(id);
      throw error;
    }
  }

  function activeSession(sessionId, chartId, sourceFingerprint) {
    expire();
    const session = sessions.get(sessionId);
    if (!session || session.seeding || session.chartId !== chartId)
      throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_EXPIRED");
    if (session.sourceFingerprint !== sourceFingerprint) {
      discard(sessionId);
      throw new LiveEngineError(409, "Calculation sources changed. Use Apply again.", "ENGINE_CHANGED");
    }
    return session;
  }

  function keepAlive({ sessionId, chartId, sourceFingerprint }) {
    activeSession(sessionId, chartId, sourceFingerprint).touched = now();
  }

  async function advance({ sessionId, chartId, sourceFingerprint, rawSha256, data }, { validate, publish }) {
    const session = activeSession(sessionId, chartId, sourceFingerprint);
    if (session.pending) {
      if (session.pending.rawSha256 === rawSha256 && session.pending.data === data) return session.pending.result;
      throw new LiveEngineError(429, "The live indicator is already updating.");
    }

    const isActive = () => {
      if (sessions.get(sessionId) !== session) throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_EXPIRED");
    };
    async function update() {
      await validate();
      isActive();
      if (session.latest?.rawSha256 !== rawSha256) {
        let payload;
        try { payload = await session.worker.update(data, rawSha256); }
        catch (error) {
          if (error.code !== "RAW_RETRY") discard(sessionId);
          throw error;
        }
        isActive();
        // Retain the full Engine result even if RAW validation, report
        // publication, or the HTTP response fails after the Engine advances.
        session.latest = { rawSha256, data, payload };
        await validate();
        isActive();
      } else if (session.latest.data !== data) {
        session.latest = { rawSha256, data, payload: session.latest.payload };
      }
      if (!session.latest.published) session.latest.published = await publish(session.latest.payload, session.request);
      return session.latest.published;
    }

    session.pending = { rawSha256, data, result: update() };
    try { return await session.pending.result; }
    finally {
      session.pending = null;
      session.touched = now();
    }
  }

  function close() {
    closed = true;
    clearInterval(timer);
    for (const id of sessions.keys()) discard(id);
  }

  return { seed, advance, keepAlive, discard, close };
}
