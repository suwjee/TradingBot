const MAX_ENGINE_CONCURRENCY = 8;
const PROGRESS_HISTORY_LIMIT = 120;

export function parseEngineConcurrency(value) {
  if (value === undefined) return 1;
  if (typeof value !== "string" || !/^[1-8]$/.test(value)) {
    throw new Error(`TRADINGBOT_MAX_ENGINE_CONCURRENCY must be an integer from 1 to ${MAX_ENGINE_CONCURRENCY}.`);
  }
  return Number(value);
}

export function createCalculationCoordinator({ maxActive = 1 } = {}) {
  if (!Number.isInteger(maxActive) || maxActive < 1 || maxActive > MAX_ENGINE_CONCURRENCY) {
    throw new Error(`Engine concurrency must be an integer from 1 to ${MAX_ENGINE_CONCURRENCY}.`);
  }

  const pending = [];
  let pendingHead = 0;
  const inFlight = new Map();
  const activeJobs = new Set();
  let closed = false;

  function publish(job, event) {
    job.events.push(event);
    if (job.events.length > PROGRESS_HISTORY_LIMIT) job.events.shift();
    for (const subscriber of job.subscribers) {
      try { subscriber(event); }
      catch { job.subscribers.delete(subscriber); }
    }
  }

  function subscribe(job, onProgress) {
    if (typeof onProgress !== "function") return;
    job.subscribers.add(onProgress);
    for (const event of job.events) {
      try { onProgress(event); }
      catch { job.subscribers.delete(onProgress); break; }
    }
  }

  // Avoid an O(n) Array.shift() for each queued request under large backlogs.
  // Clear consumed slots immediately, compact only when enough have been drained.
  function dequeuePending() {
    const job = pending[pendingHead];
    pending[pendingHead++] = undefined;
    if (pendingHead === pending.length) {
      pending.length = 0;
      pendingHead = 0;
    } else if (pendingHead >= 1024 && pendingHead * 2 >= pending.length) {
      pending.splice(0, pendingHead);
      pendingHead = 0;
    }
    return job;
  }

  function drain() {
    if (closed) return;
    while (activeJobs.size < maxActive && pendingHead < pending.length) {
      const job = dequeuePending();
      const controller = new AbortController();
      job.controller = controller;
      activeJobs.add(job);
      let result;
      try { result = job.execute((event) => publish(job, event), controller.signal); }
      catch (error) { result = Promise.reject(error); }
      Promise.resolve(result).then(
        (value) => settle(job, true, value),
        (error) => settle(job, false, error),
      );
    }
  }

  function settle(job, succeeded, value) {
    activeJobs.delete(job);
    inFlight.delete(job.key);
    job.subscribers.clear();
    job.events.length = 0;
    if (!succeeded) job.reject(value);
    else job.resolve(value);
    drain();
  }

  function run(key, execute, onProgress) {
    if (closed) return Promise.reject(new Error("Server is shutting down."));
    const existing = inFlight.get(key);
    if (existing) {
      subscribe(existing, onProgress);
      return existing.promise;
    }
    let resolve;
    let reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    const job = { key, execute, resolve, reject, promise, subscribers: new Set(), events: [], controller: null };
    subscribe(job, onProgress);
    inFlight.set(key, job);
    pending.push(job);
    drain();
    return promise;
  }

  function close() {
    if (closed) return;
    closed = true;
    const queuedJobs = pending.splice(pendingHead);
    pending.length = 0;
    pendingHead = 0;
    for (const job of queuedJobs) {
      inFlight.delete(job.key);
      job.subscribers.clear();
      job.events.length = 0;
      job.reject(new Error("Server is shutting down."));
    }
    for (const job of activeJobs) job.controller.abort();
  }

  function stats() {
    return { active: activeJobs.size, pending: pending.length - pendingHead, inFlight: inFlight.size };
  }

  return { run, close, stats };
}
