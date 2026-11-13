import type { ContentItem, ProviderInfo } from "@/lib/content/types";
import { contentId } from "@/lib/content/url";
import { fetchOEmbed } from "./oembed";
import type { ProviderAdapter, ResolveContext } from "./types";

/**
 * TikTok adapter.
 * - Metadata: public oEmbed endpoint https://www.tiktok.com/oembed?url=... (no key, verified 2026-11-13).
 * - Playback: TikTok Embed Player (https://www.tiktok.com/player/v1/{id}), the integration TikTok recommends
 *   for new builds. The player supports autoplay+muted query params and postMessage events.
 * - No feed/search: TikTok's Display API only exposes the *authenticated user's own* videos and the
 *   Research API is restricted to approved academic/non-profit research. Neither gives a public "For You" feed.
 */
export const tiktokAdapter: ProviderAdapter = {
  info: {
    id: "tiktok",
    name: "TikTok",
    accent: "#69C9D0",
    capabilities: {
      resolveUrl: true,
      feed: false,
      search: false,
      autoplay: true,
      muteControl: true,
      progressEvents: true,
    },
    status: {
      level: "partial",
      detail: "Public video URLs via oEmbed + official Embed Player. No discovery feed or search: TikTok offers no public API for that.",
    },
    requiredEnv: [],
    docsUrl: "https://developers.tiktok.com/doc/embed-player",
  } satisfies ProviderInfo,

  async resolve(externalId, canonicalUrl, ctx?: ResolveContext): Promise<ContentItem> {
    const oembed = await fetchOEmbed("tiktok", `https://www.tiktok.com/oembed?url=${encodeURIComponent(canonicalUrl)}`);
    const authorUnique = typeof oembed.author_unique_id === "string" ? oembed.author_unique_id : undefined;
    const url = authorUnique ? `https://www.tiktok.com/@${authorUnique}/video/${externalId}` : canonicalUrl;
    return {
      id: contentId("tiktok", externalId),
      provider: "tiktok",
      externalId,
      kind: "video",
      url,
      title: oembed.title?.trim() || (oembed.author_name ? `TikTok by ${oembed.author_name}` : "TikTok video"),
      authorName: oembed.author_name,
      authorUrl: oembed.author_url,
      thumbnailUrl: oembed.thumbnail_url,
      thumbnailWidth: oembed.thumbnail_width,
      thumbnailHeight: oembed.thumbnail_height,
      categories: ctx?.categories?.length ? ctx.categories : ["lifestyle"],
      embed: { type: "tiktok-player", videoId: externalId },
      origin: ctx?.origin ?? "user-submitted",
      fetchedAt: new Date().toISOString(),
    };
  },
};
