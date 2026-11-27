const API = "/api/workspace-preferences";
const STORAGE_PREFIX = "qg:workspace-preference:v1:";

export function createWorkspacePreferences({ fetcher = globalThis.fetch, storage } = {}) {
  const values = new Map();
  const saving = new Set();

  function read(key) {
    try {
      return JSON.parse(storage?.getItem(STORAGE_PREFIX + key) || "null");
    } catch {
      return null;
    }
  }

  function write(key, entry) {
    try {
      storage?.setItem(STORAGE_PREFIX + key, JSON.stringify(entry));
    } catch { /* A writable server still preserves the preference. */ }
  }

  async function save(key) {
    if (saving.has(key)) return;
    saving.add(key);
    try {
      let entry = values.get(key);
      while (entry?.pending) {
        const response = await fetcher(API, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ key, value: entry.value }),
          keepalive: true,
        });
        if (!response.ok) return;
        if (values.get(key) === entry) {
          entry.pending = false;
          if (JSON.stringify(read(key)?.value) === JSON.stringify(entry.value)) write(key, entry);
        }
        entry = values.get(key);
      }
    } catch { /* The pending browser copy can be synced on the next load. */ }
    finally { saving.delete(key); }
  }

  function get(key, fallback = null) {
    return (values.get(key) || read(key))?.value ?? fallback;
  }

  function set(key, value) {
    const snapshot = JSON.stringify(value);
    const existing = values.get(key) || read(key);
    if (existing && JSON.stringify(existing.value) === snapshot) {
      if (existing.pending) {
        values.set(key, existing);
        void save(key);
      }
      return;
    }
    const entry = { value: JSON.parse(snapshot), pending: true };
    values.set(key, entry);
    write(key, entry);
    void save(key);
  }

  async function load() {
    try {
      const response = await fetcher(API, { cache: "no-store", signal: AbortSignal.timeout(3_000) });
      if (response.ok) {
        const { preferences } = await response.json();
        for (const [key, value] of Object.entries(preferences || {})) {
          if (values.has(key) || read(key)?.pending) continue;
          const entry = { value, pending: false };
          values.set(key, entry);
          write(key, entry);
        }
      }
    } catch { /* Browser preferences remain available offline. */ }
    try {
      for (let index = 0; index < storage?.length; index++) {
        const storageKey = storage.key(index);
        if (!storageKey?.startsWith(STORAGE_PREFIX)) continue;
        const key = storageKey.slice(STORAGE_PREFIX.length);
        const entry = values.get(key) || read(key);
        if (!entry?.pending) continue;
        values.set(key, entry);
        void save(key);
      }
    } catch { /* Browser storage can be disabled. */ }
  }

  function syncStorage(storageKey) {
    if (!storageKey?.startsWith(STORAGE_PREFIX)) return null;
    const key = storageKey.slice(STORAGE_PREFIX.length);
    const entry = read(key);
    if (!entry || JSON.stringify(values.get(key)?.value) === JSON.stringify(entry.value)) return null;
    values.set(key, entry);
    return key;
  }

  return { get, set, load, syncStorage };
}
