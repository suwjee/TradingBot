const MAX_ENGINE_CONCURRENCY = 8;
const PROGRESS_HISTORY_LIMIT = 120;

export function parseEngineConcurrency(value) {
  if (value === undefined) return 1;
  if (typeof value !== "string" || !/^[1-8]$/.test(value)) {
    throw new Error(`TRADINGBOT_MAX_ENGINE_CONCURRENCY must be an integer from 1 to ${MAX_ENGINE_CONCURRENCY}.`);
  }
  return Number(value);
}

export function createCalculationWork(onAbandoned = () => {}) {
  const controller = new AbortController();
  const consumers = new Set();
  const events = [];
  let rejectAfterExit;

  function report(consumer, event) {
    try { consumer.onProgress?.(event); }
    catch { consumer.onProgress = undefined; }
  }

  function remove(consumer) {
    consumers.delete(consumer);
    consumer.signal?.removeEventListener("abort", consumer.abort);
  }

  function subscribe({ signal, onProgress } = {}) {
    if (signal?.aborted) return Promise.reject(signal.reason);
    if (controller.signal.aborted) return Promise.reject(controller.signal.reason);
    return new Promise((resolve, reject) => {
      const consumer = { signal, onProgress, resolve, reject, abort() {
        remove(consumer);
        if (consumers.size) {
          reject(signal.reason);
        } else {
          // Retain the last caller until the owned work has exited so that a
          // nested calculation cannot release its parent's slot prematurely.
          rejectAfterExit = () => reject(signal.reason);
          controller.abort(signal.reason);
          onAbandoned(signal.reason);
        }
      } };
      consumers.add(consumer);
      signal?.addEventListener("abort", consumer.abort, { once: true });
      for (const event of events) {
        if (!consumers.has(consumer)) break;
        report(consumer, event);
      }
    });
  }

  function publish(event) {
    if (controller.signal.aborted) return;
    events.push(event);
    if (events.length > PROGRESS_HISTORY_LIMIT) events.shift();
    for (const consumer of consumers) report(consumer, event);
  }

  function settle(succeeded, value) {
    for (const consumer of consumers) {
      remove(consumer);
      if (succeeded) consumer.resolve(value);
      else consumer.reject(value);
    }
    rejectAfterExit?.();
    rejectAfterExit = undefined;
    events.length = 0;
  }

  return { controller, subscribe, publish, settle };
}

export function createCalculationCoordinator({ maxActive = 1 } = {}) {
  if (!Number.isInteger(maxActive) || maxActive < 1 || maxActive > MAX_ENGINE_CONCURRENCY) {
    throw new Error(`Engine concurrency must be an integer from 1 to ${MAX_ENGINE_CONCURRENCY}.`);
  }

  const pending = [];
  const inFlight = new Map();
  const activeJobs = new Set();
  let closed = false;

  function drain() {
    if (closed) return;
    while (activeJobs.size < maxActive && pending.length) {
      const job = pending.shift();
      activeJobs.add(job);
      let result;
      try { result = job.execute(job.work.publish, job.work.controller.signal); }
      catch (error) { result = Promise.reject(error); }
      Promise.resolve(result).then(
        (value) => settle(job, true, value),
        (error) => settle(job, false, error),
      );
    }
  }

  function settle(job, succeeded, value) {
    activeJobs.delete(job);
    if (inFlight.get(job.key) === job) inFlight.delete(job.key);
    job.work.settle(succeeded, value);
    drain();
  }

  function run(key, execute, onProgress, { signal } = {}) {
    if (closed) return Promise.reject(new Error("Server is shutting down."));
    if (signal?.aborted) return Promise.reject(signal.reason);
    const existing = inFlight.get(key);
    if (existing) return existing.work.subscribe({ signal, onProgress });
    const job = { key, execute, work: createCalculationWork(reason => {
      if (inFlight.get(key) === job) inFlight.delete(key);
      const index = pending.indexOf(job);
      if (index < 0) return;
      pending.splice(index, 1);
      settle(job, false, reason);
    }) };
    const promise = job.work.subscribe({ signal, onProgress });
    inFlight.set(key, job);
    pending.push(job);
    drain();
    return promise;
  }

  function close() {
    if (closed) return;
    closed = true;
    for (const job of pending.splice(0)) settle(job, false, new Error("Server is shutting down."));
    for (const job of activeJobs) job.work.controller.abort();
  }

  function stats() {
    return { active: activeJobs.size, pending: pending.length, inFlight: inFlight.size };
  }

  return { run, close, stats };
}
