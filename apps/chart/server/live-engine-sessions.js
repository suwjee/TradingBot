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

  function receive(type, request, reportProgress) {
    if (closed) return Promise.reject(new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED"));
    if (pending) return Promise.reject(new LiveEngineError(429, "The live indicator is busy."));
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => close(new LiveEngineError(410,
        "The live Engine did not respond. Use Apply again.", "LIVE_ENGINE_TIMEOUT")), timeoutMs);
      timer.unref();
      pending = { type, resolve, reject, timer, reportProgress };
      if (request) {
        const { bytes, sha256, baseSha256 } = request;
        child.stdin.write(`${JSON.stringify({ bytes: bytes.length, sha256, baseSha256,
          ...(reportProgress && { progress: true }) })}\n`);
        child.stdin.write(bytes, error => {
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
    if (message?.type === "progress" && pending?.type === "update" && typeof message.event?.label === "string") {
      try { pending.reportProgress?.(message.event); } catch { /* Progress does not change the calculation. */ }
      return;
    }
    if (message?.type === "error") {
      if (["RAW_RETRY", "RAW_DELTA_MISMATCH"].includes(message.code)) {
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
    get closed() { return closed; },
    async update(bytes, sha256, baseSha256, reportProgress) {
      if (!Buffer.isBuffer(bytes)) throw new TypeError("The live Engine requires RAW bytes.");
      return (await receive("update", { bytes, sha256, baseSha256 }, reportProgress)).payload;
    },
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

  async function seed({ chartId, tabId, sourceFingerprint, request, rawSha256 }, launch) {
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
    const session = { worker, chartId, tabId, sourceFingerprint, request, rawSha256,
      seeding: true, touched: now() };
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

  function activeSession(sessionId, chartId, tabId, sourceFingerprint) {
    expire();
    const session = sessions.get(sessionId);
    if (!session || session.seeding || session.chartId !== chartId || session.tabId !== tabId)
      throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_EXPIRED");
    if (session.worker.closed) {
      discard(sessionId);
      throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED");
    }
    if (session.sourceFingerprint !== sourceFingerprint) {
      discard(sessionId);
      throw new LiveEngineError(409, "Calculation sources changed. Use Apply again.", "ENGINE_CHANGED");
    }
    return session;
  }

  function keepAlive({ sessionId, chartId, tabId, sourceFingerprint }) {
    activeSession(sessionId, chartId, tabId, sourceFingerprint).touched = now();
  }

  async function advance({ sessionId, chartId, tabId, sourceFingerprint, rawSha256, data }, { validate, publish, readAppend, reportProgress }) {
    const session = activeSession(sessionId, chartId, tabId, sourceFingerprint);
    if (session.pending) {
      if (session.pending.rawSha256 === rawSha256 && session.pending.data === data) return session.pending.result;
      throw new LiveEngineError(429, "The live indicator is already updating.");
    }

    const isActive = () => {
      if (sessions.get(sessionId) !== session) throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_EXPIRED");
    };
    async function update() {
      const baseSha256 = session.rawSha256;
      let delta = baseSha256 && baseSha256 !== rawSha256 && readAppend?.(baseSha256);
      let bytes = await validate(!delta, Boolean(delta));
      isActive();
      let payload;
      try {
        if (delta) {
          try { payload = await session.worker.update(delta, rawSha256, baseSha256, reportProgress); }
          catch (error) {
            if (error.code !== "RAW_DELTA_MISMATCH") throw error;
            delta = null;
            bytes = await validate(true);
            isActive();
          }
        }
        if (!delta) payload = await session.worker.update(bytes, rawSha256, undefined, reportProgress);
      } catch (error) {
        if (error.code !== "RAW_RETRY") discard(sessionId);
        throw error;
      }
      // Only the input lineage survives publication failures, so retrying
      // the same RAW starts a fresh Engine calculation.
      session.rawSha256 = rawSha256;
      await validate(false, Boolean(delta));
      isActive();
      return publish(payload, session.request);
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
