import { namedCache } from "@/lib/server/cache";
import { ProviderError } from "./types";
import type { ProviderId } from "@/lib/content/types";

export interface OEmbedResponse {
  type: "video" | "photo" | "rich" | "link";
  version: string;
  title?: string;
  author_name?: string;
  author_url?: string;
  provider_name?: string;
  provider_url?: string;
  thumbnail_url?: string;
  thumbnail_width?: number;
  thumbnail_height?: number;
  html?: string;
  width?: number | string;
  height?: number | string;
  cache_age?: number | string;
  [key: string]: unknown;
}

const USER_AGENT = "SCROLL-MVP/0.1 (+https://github.com/scroll-app)";

/**
 * Fetches an oEmbed document from an official provider endpoint, with timeout
 * and a server-side cache so we stay far below provider rate limits.
 */
export async function fetchOEmbed(
  provider: ProviderId,
  endpoint: string,
  opts: { ttlMs?: number; timeoutMs?: number } = {},
): Promise<OEmbedResponse> {
  const cache = namedCache<OEmbedResponse>("oembed");
  const cached = cache.get(endpoint);
  if (cached) return cached;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), opts.timeoutMs ?? 8000);
  let res: Response;
  try {
    res = await fetch(endpoint, {
      headers: { accept: "application/json", "user-agent": USER_AGENT },
      signal: controller.signal,
      // Let Next.js fetch cache sit underneath our TTL cache.
      cache: "no-store",
    });
  } catch (err) {
    throw new ProviderError(provider, "provider_error", `oEmbed request failed: ${(err as Error).message}`);
  } finally {
    clearTimeout(timer);
  }

  if (res.status === 404 || res.status === 400) {
    throw new ProviderError(provider, "not_found", "This publication was not found or cannot be embedded (private, deleted or restricted).");
  }
  if (res.status === 429) {
    throw new ProviderError(provider, "rate_limited", "The provider is rate-limiting embed requests. Try again shortly.");
  }
  if (!res.ok) {
    throw new ProviderError(provider, "provider_error", `oEmbed endpoint returned HTTP ${res.status}.`);
  }
  let data: OEmbedResponse;
  try {
    data = (await res.json()) as OEmbedResponse;
  } catch {
    throw new ProviderError(provider, "provider_error", "oEmbed endpoint returned an invalid response.");
  }
  cache.set(endpoint, data, opts.ttlMs ?? 6 * 60 * 60 * 1000);
  return data;
}

export function toNumber(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))) return Number(value);
  return undefined;
}

/** Extracts the first <script src> from oEmbed HTML and returns the HTML without it. */
export function splitScript(html: string): { html: string; scriptSrc?: string } {
  const match = html.match(/<script[^>]*src=["']([^"']+)["'][^>]*>\s*<\/script>/i);
  if (!match) return { html };
  let src = match[1];
  if (src.startsWith("//")) src = `https:${src}`;
  return { html: html.replace(match[0], "").trim(), scriptSrc: src };
}
