import type { ContentItem, ProviderInfo } from "@/lib/content/types";
import { contentId } from "@/lib/content/url";
import { fetchOEmbed, splitScript } from "./oembed";
import type { ProviderAdapter, ResolveContext } from "./types";

/**
 * X (Twitter) adapter.
 * - Metadata + embed: public oEmbed endpoint https://publish.x.com/oembed (no key, verified 2026-11-13).
 * - Playback: X's official widgets.js embedded timeline/post. Video inside posts is controlled by X's widget.
 * - No feed/search: the X API no longer has a free tier for new developers (pay-per-use since 2026),
 *   so discovery/search are intentionally not implemented in the MVP.
 */
export const xAdapter: ProviderAdapter = {
  info: {
    id: "x",
    name: "X",
    accent: "#FFFFFF",
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
      detail: "Public posts via oEmbed + official embed widget. No feed or search: the X API is paid-only for new apps.",
    },
    requiredEnv: [],
    docsUrl: "https://developer.x.com/en/docs/x-for-websites/oembed-api",
  } satisfies ProviderInfo,

  async resolve(externalId, canonicalUrl, ctx?: ResolveContext): Promise<ContentItem> {
    const endpoint = new URL("https://publish.x.com/oembed");
    endpoint.searchParams.set("url", canonicalUrl);
    endpoint.searchParams.set("omit_script", "true");
    endpoint.searchParams.set("theme", "dark");
    endpoint.searchParams.set("dnt", "true");
    endpoint.searchParams.set("maxwidth", "550");
    const oembed = await fetchOEmbed("x", endpoint.toString());
    const { html } = splitScript(oembed.html ?? "");
    const text = html
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    const handle = oembed.author_url?.split("/").filter(Boolean).pop();
    return {
      id: contentId("x", externalId),
      provider: "x",
      externalId,
      kind: "post",
      url: typeof oembed.url === "string" ? oembed.url : canonicalUrl,
      title: text ? text.slice(0, 140) : `Post by ${oembed.author_name ?? "user"}`,
      description: text || undefined,
      authorName: handle ? `@${handle}` : oembed.author_name,
      authorUrl: oembed.author_url,
      categories: ctx?.categories?.length ? ctx.categories : ["news"],
      embed: { type: "oembed-html", html, scriptSrc: "https://platform.twitter.com/widgets.js" },
      origin: ctx?.origin ?? "user-submitted",
      fetchedAt: new Date().toISOString(),
    };
  },
};
