/**
 * Tiny in-memory TTL cache for server runtime. Good enough for a single Node
 * instance; swap for Redis/Upstash when scaling horizontally (see docs/architecture.md).
 */
interface Entry<T> {
  value: T;
  expiresAt: number;
}

export class TtlCache<T> {
  private readonly map = new Map<string, Entry<T>>();
  constructor(private readonly maxEntries = 2000) {}

  get(key: string): T | undefined {
    const entry = this.map.get(key);
    if (!entry) return undefined;
    if (entry.expiresAt < Date.now()) {
      this.map.delete(key);
      return undefined;
    }
    // Refresh LRU position
    this.map.delete(key);
    this.map.set(key, entry);
    return entry.value;
  }

  set(key: string, value: T, ttlMs: number): void {
    if (this.map.size >= this.maxEntries) {
      const oldest = this.map.keys().next().value;
      if (oldest !== undefined) this.map.delete(oldest);
    }
    this.map.set(key, { value, expiresAt: Date.now() + ttlMs });
  }

  delete(key: string): void {
    this.map.delete(key);
  }

  get size(): number {
    return this.map.size;
  }
}

declare global {
  var __scrollCaches: Map<string, TtlCache<unknown>> | undefined;
}

/** Returns a process-wide named cache that survives HMR in development. */
export function namedCache<T>(name: string, maxEntries = 2000): TtlCache<T> {
  if (!globalThis.__scrollCaches) globalThis.__scrollCaches = new Map();
  let cache = globalThis.__scrollCaches.get(name) as TtlCache<T> | undefined;
  if (!cache) {
    cache = new TtlCache<T>(maxEntries);
    globalThis.__scrollCaches.set(name, cache as TtlCache<unknown>);
  }
  return cache;
}
