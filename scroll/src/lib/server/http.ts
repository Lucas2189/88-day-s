import { NextResponse } from "next/server";
import type { ApiError } from "@/lib/content/types";
import { ProviderError } from "@/lib/providers/types";
import { clientKey, rateLimit } from "./rate-limit";

export function jsonError(code: ApiError["code"], error: string, status: number, extra: Partial<ApiError> = {}) {
  return NextResponse.json({ error, code, ...extra } satisfies ApiError, { status });
}

export function errorFromProvider(err: unknown) {
  if (err instanceof ProviderError) {
    const status = err.code === "not_found" ? 404 : err.code === "rate_limited" ? 429 : err.code === "unsupported" ? 422 : 502;
    const code: ApiError["code"] = err.code === "unsupported" ? "unsupported_provider" : err.code;
    return jsonError(code, err.message, status, { provider: err.provider });
  }
  console.error("[api] unexpected error", err);
  return jsonError("provider_error", "Unexpected server error.", 500);
}

/** Applies a per-client limiter; returns a 429 response when exceeded. */
export function enforceRateLimit(request: Request, bucket: string, capacity: number, refillPerSecond: number) {
  const result = rateLimit(`${bucket}:${clientKey(request)}`, { capacity, refillPerSecond });
  if (!result.ok) {
    const res = jsonError("rate_limited", "Too many requests. Please slow down.", 429);
    res.headers.set("retry-after", String(result.retryAfterSeconds));
    return res;
  }
  return null;
}
