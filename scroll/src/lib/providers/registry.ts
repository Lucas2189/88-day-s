import type { ContentItem, ProviderId, ProviderInfo } from "@/lib/content/types";
import { parseContentUrl } from "@/lib/content/url";
import { instagramAdapter } from "./instagram";
import { redditAdapter } from "./reddit";
import { tiktokAdapter } from "./tiktok";
import { ProviderError, type ProviderAdapter, type ResolveContext } from "./types";
import { xAdapter } from "./x";
import { youtubeAdapter } from "./youtube";

const adapters: Record<ProviderId, ProviderAdapter> = {
  youtube: youtubeAdapter,
  tiktok: tiktokAdapter,
  instagram: instagramAdapter,
  x: xAdapter,
  reddit: redditAdapter,
};

export function getAdapter(id: ProviderId): ProviderAdapter {
  return adapters[id];
}

export function listProviderInfo(): ProviderInfo[] {
  return (Object.keys(adapters) as ProviderId[]).map((id) => adapters[id].info);
}

/** Resolves any supported public URL via the matching adapter. */
export async function resolveUrl(input: string, ctx?: ResolveContext): Promise<ContentItem> {
  const parsed = parseContentUrl(input);
  if (!parsed) {
    throw new ProviderError("youtube", "unsupported", "Unsupported or invalid URL. Paste a public YouTube, TikTok, Instagram, X or Reddit link.");
  }
  const adapter = adapters[parsed.provider];
  return adapter.resolve(parsed.externalId, parsed.canonicalUrl, ctx);
}

export { ProviderError };
