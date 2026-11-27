import { scrubDiagnostic } from "./diagnostic-details.js";

const API = "/api/error-journal";
const KEY = "tradingbot:error-outbox:";

export function createErrorJournalClient({ storage, fetcher = globalThis.fetch, changed }) {
  const pending = new Map();
  const saved = new Map();
  let queue = Promise.resolve();

  function notify() {
    const entries = new Map([...pending, ...saved]);
    changed([...entries.values()].sort((a, b) => b.recordedAt - a.recordedAt));
  }

  function storageKeys() {
    try { return Array.from({ length: storage?.length ?? 0 }, (_, i) => storage.key(i)).filter(key => key?.startsWith(KEY)); }
    catch { return []; }
  }

  function enqueue(operation) {
    const result = queue.then(operation);
    queue = result.catch(() => {});
    return result;
  }

  async function flush() {
    for (const [id, entry] of pending) {
      const response = await fetcher(API, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(entry), signal: AbortSignal.timeout(5_000) });
      if (!response.ok) throw new Error(`Error journal save HTTP ${response.status}`);
      pending.delete(id);
      saved.set(id, entry);
      try { storage?.removeItem(KEY + id); } catch { /* server copy is durable */ }
    }
  }

  function record(input) {
    const entry = scrubDiagnostic(input);
    pending.set(entry.id, entry);
    try { storage?.setItem(KEY + entry.id, JSON.stringify(entry)); } catch { /* try the server copy below */ }
    notify();
    return enqueue(flush);
  }

  function reload() {
    return enqueue(async () => {
      for (const key of storageKeys()) {
        try {
          const entry = JSON.parse(storage.getItem(key));
          if (entry?.id) pending.set(entry.id, entry);
        } catch { /* preserve the outbox entry */ }
      }
      notify();
      const response = await fetcher(API, { cache: "no-store", signal: AbortSignal.timeout(5_000) });
      if (!response.ok) throw new Error(`Error journal load HTTP ${response.status}`);
      const { entries } = await response.json();
      saved.clear();
      for (const entry of entries) saved.set(entry.id, entry);
      notify();
      await flush();
    });
  }

  function clear() {
    return enqueue(async () => {
      const response = await fetcher(API, { method: "DELETE", signal: AbortSignal.timeout(5_000) });
      if (!response.ok) throw new Error(`Error journal clear HTTP ${response.status}`);
      for (const key of storageKeys()) {
        try { storage.removeItem(key); } catch { /* reachable records can be cleared */ }
      }
      pending.clear();
      saved.clear();
      notify();
    });
  }

  return { record, reload, clear };
}
