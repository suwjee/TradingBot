import { spawn } from "node:child_process";
import { randomBytes } from "node:crypto";
import { createInterface } from "node:readline";
import { createCalculationWork } from "./calculation-coordinator.js";

const EXPIRED = "The live indicator session is unavailable. Use Apply again.";

export class LiveEngineError extends Error {
  constructor(status, message, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function startLiveEngineWorker({ command, args, env, onProgress, signal, timeoutMs = 300_000 }) {
  signal?.throwIfAborted();
  const child = spawn(command, args, { env, windowsHide: true });
  const exited = new Promise(resolve => child.once("close", resolve));
  const output = createInterface({ input: child.stdout, crlfDelay: Infinity });
  child.stderr.resume();
  let pending;
  let closed = false;

  function settle(error, message) {
    if (!pending) return;
    const { resolve, reject, timer, taskSignal, abort } = pending;
    pending = null;
    clearTimeout(timer);
    taskSignal?.removeEventListener("abort", abort);
    if (error) reject(error);
    else resolve(message);
  }

  function close(error = new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED")) {
    if (closed) return;
    closed = true;
    settle(error);
    output.close();
    child.kill();
  }

  async function receive(type, request, reportProgress, taskSignal) {
    taskSignal?.throwIfAborted();
    if (closed) throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_CLOSED");
    if (pending) throw new LiveEngineError(429, "The live indicator is busy.");
    try {
      return await new Promise((resolve, reject) => {
        const timer = setTimeout(() => close(new LiveEngineError(410,
          "The live Engine did not respond. Use Apply again.", "LIVE_ENGINE_TIMEOUT")), timeoutMs);
        timer.unref();
        const abort = () => close(taskSignal.reason);
        pending = { type, resolve, reject, timer, reportProgress, taskSignal, abort };
        taskSignal?.addEventListener("abort", abort, { once: true });
        if (request) {
          const { bytes, sha256, baseSha256 } = request;
          child.stdin.write(`${JSON.stringify({ bytes: bytes.length, sha256, baseSha256,
            ...(reportProgress && { progress: true }) })}\n`);
          child.stdin.write(bytes, error => {
            if (error) close();
          });
        }
      });
    } catch (error) {
      if (closed) await exited;
      throw error;
    }
  }

  output.on("line", line => {
    let message;
    try { message = JSON.parse(line); }
    catch {
      close(new LiveEngineError(410, "The live Engine returned an invalid response.", "LIVE_ENGINE_PROTOCOL"));
      return;
    }
    if (message?.type === "progress" && pending && typeof message.event?.label === "string") {
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
    settle(null, message);
  });
  child.on("error", () => close());
  child.stdin.on("error", () => close());
  child.on("close", () => close());

  const seed = receive("seed", undefined, onProgress, signal);
  return {
    seed,
    get closed() { return closed; },
    async update(bytes, sha256, baseSha256, reportProgress, taskSignal) {
      if (!Buffer.isBuffer(bytes)) throw new TypeError("The live Engine requires RAW bytes.");
      return (await receive("update", { bytes, sha256, baseSha256 }, reportProgress, taskSignal)).payload;
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

  async function advance({ sessionId, chartId, tabId, sourceFingerprint, rawSha256, data }, {
    validate, publish, readAppend, reportProgress, signal, schedule = work => work(),
  }) {
    signal?.throwIfAborted();
    const session = activeSession(sessionId, chartId, tabId, sourceFingerprint);
    const consumer = { signal, onProgress: reportProgress };
    if (session.pending) {
      const { work } = session.pending;
      if (!work.controller.signal.aborted && session.pending.rawSha256 === rawSha256 && session.pending.data === data) {
        session.pending.reportProgress ||= Boolean(reportProgress);
        return work.subscribe(consumer);
      }
      throw new LiveEngineError(429, "The live indicator is already updating.");
    }

    const work = createCalculationWork();
    const pending = { rawSha256, data, work, reportProgress: Boolean(reportProgress) };
    session.pending = pending;
    const result = work.subscribe(consumer);

    const isActive = () => {
      if (sessions.get(sessionId) !== session) throw new LiveEngineError(410, EXPIRED, "LIVE_SESSION_EXPIRED");
    };
    async function update(_progress, taskSignal = work.controller.signal) {
      taskSignal.throwIfAborted();
      isActive();
      const baseSha256 = session.rawSha256;
      let delta = baseSha256 && baseSha256 !== rawSha256 && readAppend?.(baseSha256);
      let bytes = await validate(!delta, Boolean(delta), taskSignal);
      taskSignal.throwIfAborted();
      isActive();
      const report = pending.reportProgress ? work.publish : undefined;
      let payload;
      try {
        if (delta) {
          try { payload = await session.worker.update(delta, rawSha256, baseSha256, report, taskSignal); }
          catch (error) {
            if (error.code !== "RAW_DELTA_MISMATCH") throw error;
            delta = null;
            bytes = await validate(true, false, taskSignal);
            taskSignal.throwIfAborted();
            isActive();
          }
        }
        if (!delta) payload = await session.worker.update(bytes, rawSha256, undefined, report, taskSignal);
      } catch (error) {
        if (error.code !== "RAW_RETRY") discard(sessionId);
        throw error;
      }
      // Only the input lineage survives publication failures, so retrying
      // the same RAW starts a fresh Engine calculation.
      session.rawSha256 = rawSha256;
      await validate(false, Boolean(delta), taskSignal);
      taskSignal.throwIfAborted();
      isActive();
      return publish(payload, session.request);
    }

    function finish(succeeded, value) {
      session.pending = null;
      session.touched = now();
      work.settle(succeeded, value);
    }
    try {
      Promise.resolve(schedule(update, { signal: work.controller.signal }))
        .then(value => finish(true, value), error => finish(false, error));
    } catch (error) {
      finish(false, error);
    }
    return result;
  }

  function close() {
    closed = true;
    clearInterval(timer);
    for (const id of sessions.keys()) discard(id);
  }

  return { seed, advance, keepAlive, discard, close };
}
