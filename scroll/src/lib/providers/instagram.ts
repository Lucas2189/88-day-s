import type { ContentItem, ProviderInfo } from "@/lib/content/types";
import { contentId } from "@/lib/content/url";
import { fetchOEmbed, splitScript } from "./oembed";
import type { ProviderAdapter, ResolveContext } from "./types";

/**
 * Instagram adapter.
 * - Metadata + embed: Meta oEmbed endpoint. Since 2026-06-15 Meta allows tokenless calls for public content
 *   (developers.facebook.com blog, verified 2026-11-13). Providing META_APP_ID/META_CLIENT_TOKEN (app access
 *   token) raises the rate limit; without it Meta documents ~1,000 requests/endpoint/hour.
 * - Playback: Instagram's official embed.js (blockquote). Autoplay/mute are controlled by Instagram's embed,
 *   not by SCROLL, so we do not advertise autoplay for this provider.
 * - No feed/search: the Instagram Graph API only covers content owned by connected professional accounts.
 */
const GRAPH_VERSION = "v25.0";

function accessToken(): string | undefined {
  const appId = process.env.META_APP_ID?.trim();
  const clientToken = process.env.META_CLIENT_TOKEN?.trim();
  if (appId && clientToken) return `${appId}|${clientToken}`;
  return undefined;
}

export const instagramAdapter: ProviderAdapter = {
  get info(): ProviderInfo {
    return {
      id: "instagram",
      name: "Instagram",
      accent: "#E1306C",
      capabilities: {
        resolveUrl: true,
        feed: false,
        search: false,
        autoplay: false,
        muteControl: false,
        progressEvents: false,
      },
      status: {
        level: "partial",
        detail: accessToken()
          ? "Public posts & Reels via Meta oEmbed (app token). No feed or search API for public content."
          : "Public posts & Reels via Meta oEmbed (tokenless, lower rate limit). No feed or search API for public content.",
      },
      requiredEnv: ["META_APP_ID (optional)", "META_CLIENT_TOKEN (optional)"],
      docsUrl: "https://developers.facebook.com/docs/instagram-platform/oembed",
    };
  },

  async resolve(externalId, canonicalUrl, ctx?: ResolveContext): Promise<ContentItem> {
    const endpoint = new URL(`https://graph.facebook.com/${GRAPH_VERSION}/instagram_oembed`);
    endpoint.searchParams.set("url", canonicalUrl);
    endpoint.searchParams.set("omitscript", "true");
    endpoint.searchParams.set("maxwidth", "540");
    const token = accessToken();
    if (token) endpoint.searchParams.set("access_token", token);
    const oembed = await fetchOEmbed("instagram", endpoint.toString());
    const { html } = splitScript(oembed.html ?? "");
    const isReel = canonicalUrl.includes("/reel/");
    return {
      id: contentId("instagram", externalId),
      provider: "instagram",
      externalId,
      kind: isReel ? "video" : "post",
      url: canonicalUrl,
      title: oembed.title?.trim() || `Instagram ${isReel ? "Reel" : "post"} by ${oembed.author_name ?? "creator"}`,
      authorName: oembed.author_name,
      authorUrl: oembed.author_url ?? (oembed.author_name ? `https://www.instagram.com/${oembed.author_name}/` : undefined),
      thumbnailUrl: oembed.thumbnail_url,
      thumbnailWidth: oembed.thumbnail_width,
      thumbnailHeight: oembed.thumbnail_height,
      categories: ctx?.categories?.length ? ctx.categories : ["lifestyle"],
      embed: { type: "oembed-html", html, scriptSrc: "https://www.instagram.com/embed.js" },
      origin: ctx?.origin ?? "user-submitted",
      fetchedAt: new Date().toISOString(),
    };
  },
};
