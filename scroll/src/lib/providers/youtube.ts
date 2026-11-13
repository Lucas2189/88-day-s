import type { CategoryId, ContentItem, ProviderInfo } from "@/lib/content/types";
import { contentId } from "@/lib/content/url";
import { fetchOEmbed } from "./oembed";
import { ProviderError, type FeedOptions, type ProviderAdapter, type ResolveContext, type SearchOptions } from "./types";
import { namedCache } from "@/lib/server/cache";

/**
 * YouTube adapter.
 * - Metadata: public oEmbed endpoint (no key) + optional Data API v3 (videos.list, playlistItems.list, search.list).
 * - Playback: official IFrame Player API (muted autoplay, user-initiated unmute).
 * Quota notes (verified 2026-11-13 on developers.google.com): default 10,000 units/day shared, plus a separate
 * allocation of 100 search.list calls/day. We therefore never call search.list on the feed path.
 */

const apiKey = () => process.env.YOUTUBE_API_KEY?.trim() || undefined;

/** YouTube categoryId → SCROLL category mapping (from videoCategories.list, US region). */
const YT_CATEGORY_MAP: Record<string, CategoryId> = {
  "1": "film",
  "2": "tech", // Autos & Vehicles → closest bucket
  "10": "music",
  "15": "animals",
  "17": "sports",
  "19": "travel",
  "20": "gaming",
  "22": "lifestyle",
  "23": "comedy",
  "24": "lifestyle", // Entertainment
  "25": "news",
  "26": "lifestyle", // Howto & Style
  "27": "education",
  "28": "science",
};

interface YtVideoResource {
  id: string;
  snippet?: {
    title?: string;
    description?: string;
    channelTitle?: string;
    channelId?: string;
    publishedAt?: string;
    categoryId?: string;
    tags?: string[];
    thumbnails?: Record<string, { url: string; width: number; height: number }>;
  };
  contentDetails?: { duration?: string };
  statistics?: { viewCount?: string; likeCount?: string };
}

function parseIsoDuration(iso?: string): number | undefined {
  if (!iso) return undefined;
  const m = iso.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!m) return undefined;
  return Number(m[1] ?? 0) * 3600 + Number(m[2] ?? 0) * 60 + Number(m[3] ?? 0);
}

async function dataApi<T>(path: string, params: Record<string, string>): Promise<T> {
  const key = apiKey();
  if (!key) throw new ProviderError("youtube", "unsupported", "YOUTUBE_API_KEY is not configured.");
  const url = new URL(`https://www.googleapis.com/youtube/v3/${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  url.searchParams.set("key", key);
  const cache = namedCache<unknown>("youtube-data-api");
  const cacheKey = url.toString().replace(key, "KEY");
  const hit = cache.get(cacheKey);
  if (hit) return hit as T;
  const res = await fetch(url, { cache: "no-store", headers: { accept: "application/json" } });
  if (res.status === 403 || res.status === 429) {
    throw new ProviderError("youtube", "rate_limited", "YouTube Data API quota exceeded or key not authorized.");
  }
  if (!res.ok) throw new ProviderError("youtube", "provider_error", `YouTube Data API returned HTTP ${res.status}.`);
  const json = (await res.json()) as T;
  cache.set(cacheKey, json, 30 * 60 * 1000);
  return json;
}

function fromVideoResource(v: YtVideoResource, origin: ContentItem["origin"], hints?: CategoryId[]): ContentItem {
  const thumbs = v.snippet?.thumbnails ?? {};
  const best = thumbs.maxres ?? thumbs.standard ?? thumbs.high ?? thumbs.medium ?? thumbs.default;
  const mapped = v.snippet?.categoryId ? YT_CATEGORY_MAP[v.snippet.categoryId] : undefined;
  const categories = Array.from(new Set([...(hints ?? []), ...(mapped ? [mapped] : [])]));
  return {
    id: contentId("youtube", v.id),
    provider: "youtube",
    externalId: v.id,
    kind: "video",
    url: `https://www.youtube.com/watch?v=${v.id}`,
    title: v.snippet?.title ?? "YouTube video",
    description: v.snippet?.description?.slice(0, 400),
    authorName: v.snippet?.channelTitle,
    authorUrl: v.snippet?.channelId ? `https://www.youtube.com/channel/${v.snippet.channelId}` : undefined,
    thumbnailUrl: best?.url,
    thumbnailWidth: best?.width,
    thumbnailHeight: best?.height,
    durationSeconds: parseIsoDuration(v.contentDetails?.duration),
    publishedAt: v.snippet?.publishedAt,
    categories: categories.length ? categories : ["lifestyle"],
    tags: v.snippet?.tags?.slice(0, 10),
    embed: { type: "youtube-player", videoId: v.id },
    origin,
    fetchedAt: new Date().toISOString(),
    extras: {
      viewCount: v.statistics?.viewCount ? Number(v.statistics.viewCount) : null,
      likeCount: v.statistics?.likeCount ? Number(v.statistics.likeCount) : null,
    },
  };
}

export const youtubeAdapter: ProviderAdapter = {
  get info(): ProviderInfo {
    const hasKey = Boolean(apiKey());
    return {
      id: "youtube",
      name: "YouTube",
      accent: "#FF0033",
      capabilities: {
        resolveUrl: true,
        feed: hasKey,
        search: hasKey,
        autoplay: true,
        muteControl: true,
        progressEvents: true,
      },
      status: hasKey
        ? { level: "live", detail: "oEmbed + Data API v3 (videos, playlists, limited search) + IFrame Player API." }
        : { level: "partial", detail: "oEmbed + IFrame Player API. Add YOUTUBE_API_KEY for channel feeds and search." },
      requiredEnv: ["YOUTUBE_API_KEY (optional)", "YOUTUBE_FEED_PLAYLIST_IDS (optional)"],
      docsUrl: "https://developers.google.com/youtube/iframe_api_reference",
    };
  },

  async resolve(externalId, canonicalUrl, ctx?: ResolveContext) {
    // Prefer Data API when available (duration, category, stats are allowed to be displayed).
    if (apiKey()) {
      const data = await dataApi<{ items?: YtVideoResource[] }>("videos", {
        part: "snippet,contentDetails,statistics",
        id: externalId,
      });
      const v = data.items?.[0];
      if (!v) throw new ProviderError("youtube", "not_found", "Video not found or not public.");
      return fromVideoResource(v, ctx?.origin ?? "user-submitted", ctx?.categories);
    }
    const oembed = await fetchOEmbed(
      "youtube",
      `https://www.youtube.com/oembed?url=${encodeURIComponent(canonicalUrl)}&format=json`,
    );
    return {
      id: contentId("youtube", externalId),
      provider: "youtube",
      externalId,
      kind: "video",
      url: canonicalUrl,
      title: oembed.title ?? "YouTube video",
      authorName: oembed.author_name,
      authorUrl: oembed.author_url,
      thumbnailUrl: oembed.thumbnail_url,
      thumbnailWidth: oembed.thumbnail_width,
      thumbnailHeight: oembed.thumbnail_height,
      categories: ctx?.categories?.length ? ctx.categories : ["lifestyle"],
      embed: { type: "youtube-player", videoId: externalId },
      origin: ctx?.origin ?? "user-submitted",
      fetchedAt: new Date().toISOString(),
    };
  },

  /** Discovery feed from configured public playlists (1 quota unit per page). */
  async feed(opts: FeedOptions) {
    const playlistIds = (process.env.YOUTUBE_FEED_PLAYLIST_IDS ?? "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!apiKey() || playlistIds.length === 0) return [];
    const ids: string[] = [];
    for (const playlistId of playlistIds.slice(0, 4)) {
      const page = await dataApi<{ items?: { contentDetails?: { videoId?: string } }[] }>("playlistItems", {
        part: "contentDetails",
        playlistId,
        maxResults: "25",
      });
      for (const it of page.items ?? []) if (it.contentDetails?.videoId) ids.push(it.contentDetails.videoId);
    }
    if (ids.length === 0) return [];
    const videos = await dataApi<{ items?: YtVideoResource[] }>("videos", {
      part: "snippet,contentDetails,statistics",
      id: ids.slice(0, 50).join(","),
    });
    return (videos.items ?? [])
      .map((v) => fromVideoResource(v, "provider-api"))
      .filter((it) => !opts.categories?.length || it.categories.some((c) => opts.categories!.includes(c)))
      .slice(0, opts.limit ?? 50);
  },

  /** search.list is limited to 100 calls/day by default: used only for explicit user searches. */
  async search(opts: SearchOptions) {
    if (!apiKey()) return [];
    const result = await dataApi<{ items?: { id?: { videoId?: string } }[] }>("search", {
      part: "id",
      type: "video",
      videoEmbeddable: "true",
      maxResults: String(Math.min(opts.limit ?? 12, 25)),
      q: opts.query,
      safeSearch: "moderate",
    });
    const ids = (result.items ?? []).map((i) => i.id?.videoId).filter((v): v is string => Boolean(v));
    if (ids.length === 0) return [];
    const videos = await dataApi<{ items?: YtVideoResource[] }>("videos", {
      part: "snippet,contentDetails,statistics",
      id: ids.join(","),
    });
    return (videos.items ?? []).map((v) => fromVideoResource(v, "provider-api"));
  },
};
