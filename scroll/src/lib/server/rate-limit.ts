/**
 * Token-bucket rate limiter keyed by client identifier (IP). In-memory; the
 * same caveat as cache.ts applies for multi-instance deployments.
 */
import { namedCache } from "./cache";

interface Bucket {
  tokens: number;
  updatedAt: number;
}

export interface RateLimitResult {
  ok: boolean;
  remaining: number;
  retryAfterSeconds: number;
}

export function rateLimit(key: string, opts: { capacity: number; refillPerSecond: number }): RateLimitResult {
  const cache = namedCache<Bucket>("rate-limit", 10_000);
  const now = Date.now();
  const bucket = cache.get(key) ?? { tokens: opts.capacity, updatedAt: now };
  const elapsed = (now - bucket.updatedAt) / 1000;
  bucket.tokens = Math.min(opts.capacity, bucket.tokens + elapsed * opts.refillPerSecond);
  bucket.updatedAt = now;
  if (bucket.tokens < 1) {
    cache.set(key, bucket, 60_000);
    return { ok: false, remaining: 0, retryAfterSeconds: Math.ceil((1 - bucket.tokens) / opts.refillPerSecond) };
  }
  bucket.tokens -= 1;
  cache.set(key, bucket, 60_000);
  return { ok: true, remaining: Math.floor(bucket.tokens), retryAfterSeconds: 0 };
}

export function clientKey(request: Request): string {
  const fwd = request.headers.get("x-forwarded-for");
  const ip = fwd?.split(",")[0]?.trim() || request.headers.get("x-real-ip") || "anonymous";
  return ip;
}
