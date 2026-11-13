import type { CategoryId, ContentItem, ProviderInfo } from "@/lib/content/types";
import { contentId } from "@/lib/content/url";
import { namedCache } from "@/lib/server/cache";
import { ProviderError, type FeedOptions, type ProviderAdapter, type ResolveContext, type SearchOptions } from "./types";

/**
 * Reddit adapter.
 * - Without credentials: public post URLs render through Reddit's official embed widget
 *   (embed.reddit.com/widgets.js). Metadata is limited to what the URL carries, and is labeled as such.
 * - With REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET (a registered, approved "script"/"web" app, OAuth client
 *   credentials): resolve, subreddit feeds and search through oauth.reddit.com within the free-tier limit
 *   (100 QPM per client). Reddit requires registration/approval and prohibits commercial use without a
 *   written agreement: see docs/feasibility.md.
 */
const USER_AGENT = "web:scroll-aggregator-mvp:0.1 (by /u/scroll-mvp)";

function creds() {
  const id = process.env.REDDIT_CLIENT_ID?.trim();
  const secret = process.env.REDDIT_CLIENT_SECRET?.trim();
  return id && secret ? { id, secret } : undefined;
}

interface Token {
  value: string;
  expiresAt: number;
}

async function accessToken(): Promise<string> {
  const c = creds();
  if (!c) throw new ProviderError("reddit", "unsupported", "Reddit API credentials are not configured.");
  const cache = namedCache<Token>("reddit-token");
  const hit = cache.get("token");
  if (hit && hit.expiresAt > Date.now() + 30_000) return hit.value;
  const res = await fetch("https://www.reddit.com/api/v1/access_token", {
    method: "POST",
    headers: {
      authorization: `Basic ${Buffer.from(`${c.id}:${c.secret}`).toString("base64")}`,
      "content-type": "application/x-www-form-urlencoded",
      "user-agent": USER_AGENT,
    },
    body: "grant_type=client_credentials",
    cache: "no-store",
  });
  if (!res.ok) throw new ProviderError("reddit", "provider_error", `Reddit OAuth failed with HTTP ${res.status}.`);
  const json = (await res.json()) as { access_token: string; expires_in: number };
  const token = { value: json.access_token, expiresAt: Date.now() + json.expires_in * 1000 };
  cache.set("token", token, json.expires_in * 1000);
  return token.value;
}

interface RedditPost {
  id: string;
  title: string;
  author: string;
  subreddit: string;
  permalink: string;
  url?: string;
  created_utc: number;
  is_video?: boolean;
  over_18?: boolean;
  selftext?: string;
  thumbnail?: string;
  preview?: { images?: { source?: { url: string; width: number; height: number } }[] };
  media?: { reddit_video?: { duration?: number } };
  score?: number;
  num_comments?: number;
}

async function api<T>(path: string, params: Record<string, string>): Promise<T> {
  const token = await accessToken();
  const url = new URL(`https://oauth.reddit.com${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  url.searchParams.set("raw_json", "1");
  const cache = namedCache<unknown>("reddit-api");
  const hit = cache.get(url.toString());
  if (hit) return hit as T;
  const res = await fetch(url, { headers: { authorization: `Bearer ${token}`, "user-agent": USER_AGENT }, cache: "no-store" });
  if (res.status === 429) throw new ProviderError("reddit", "rate_limited", "Reddit API rate limit reached.");
  if (res.status === 404) throw new ProviderError("reddit", "not_found", "Reddit post not found.");
  if (!res.ok) throw new ProviderError("reddit", "provider_error", `Reddit API returned HTTP ${res.status}.`);
  const json = (await res.json()) as T;
  cache.set(url.toString(), json, 5 * 60 * 1000);
  return json;
}

const SUBREDDIT_CATEGORIES: Record<string, CategoryId> = {
  videos: "lifestyle",
  funny: "comedy",
  gaming: "gaming",
  technology: "tech",
  science: "science",
  sports: "sports",
  food: "food",
  travel: "travel",
  art: "art",
  aww: "animals",
  worldnews: "news",
  movies: "film",
  todayilearned: "education",
  music: "music",
};

function embedHtml(url: string): string {
  return `<blockquote class="reddit-embed-bq" data-embed-theme="dark" data-embed-height="560"><a href="${url}">View this post on Reddit</a></blockquote>`;
}

function fromPost(p: RedditPost, origin: ContentItem["origin"], hints?: CategoryId[]): ContentItem {
  const url = `https://www.reddit.com${p.permalink}`;
  const preview = p.preview?.images?.[0]?.source;
  const cat = SUBREDDIT_CATEGORIES[p.subreddit.toLowerCase()];
  const categories = Array.from(new Set([...(hints ?? []), ...(cat ? [cat] : [])]));
  return {
    id: contentId("reddit", p.id),
    provider: "reddit",
    externalId: p.id,
    kind: p.is_video ? "video" : "post",
    url,
    title: p.title,
    description: p.selftext?.slice(0, 400) || undefined,
    authorName: `u/${p.author} · r/${p.subreddit}`,
    authorUrl: `https://www.reddit.com/r/${p.subreddit}/`,
    thumbnailUrl: preview?.url,
    thumbnailWidth: preview?.width,
    thumbnailHeight: preview?.height,
    durationSeconds: p.media?.reddit_video?.duration,
    publishedAt: new Date(p.created_utc * 1000).toISOString(),
    categories: categories.length ? categories : ["lifestyle"],
    embed: { type: "oembed-html", html: embedHtml(url), scriptSrc: "https://embed.reddit.com/widgets.js" },
    origin,
    fetchedAt: new Date().toISOString(),
    extras: { score: p.score ?? null, comments: p.num_comments ?? null, subreddit: p.subreddit },
  };
}

export const redditAdapter: ProviderAdapter = {
  get info(): ProviderInfo {
    const live = Boolean(creds());
    return {
      id: "reddit",
      name: "Reddit",
      accent: "#FF4500",
      capabilities: {
        resolveUrl: true,
        feed: live,
        search: live,
        autoplay: false,
        muteControl: false,
        progressEvents: false,
      },
      status: live
        ? { level: "live", detail: "Data API (OAuth app) for subreddit feeds and search + official embed widget." }
        : {
            level: "partial",
            detail: "Public post URLs via Reddit's official embed widget. Add approved Reddit API credentials for feeds and search.",
          },
      requiredEnv: ["REDDIT_CLIENT_ID (optional)", "REDDIT_CLIENT_SECRET (optional)", "REDDIT_FEED_SUBREDDITS (optional)"],
      docsUrl: "https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki",
    };
  },

  async resolve(externalId, canonicalUrl, ctx?: ResolveContext): Promise<ContentItem> {
    if (creds()) {
      const data = await api<{ data?: { children?: { data: RedditPost }[] } }>("/api/info", { id: `t3_${externalId}` });
      const post = data.data?.children?.[0]?.data;
      if (!post) throw new ProviderError("reddit", "not_found", "Reddit post not found.");
      return fromPost(post, ctx?.origin ?? "user-submitted", ctx?.categories);
    }
    const subMatch = canonicalUrl.match(/\/r\/([^/]+)\//);
    const cat = subMatch ? SUBREDDIT_CATEGORIES[subMatch[1].toLowerCase()] : undefined;
    return {
      id: contentId("reddit", externalId),
      provider: "reddit",
      externalId,
      kind: "post",
      url: canonicalUrl,
      title: subMatch ? `Reddit post in r/${subMatch[1]}` : "Reddit post",
      description: "Metadata unavailable without Reddit API credentials. The post renders through Reddit's official embed.",
      authorName: subMatch ? `r/${subMatch[1]}` : undefined,
      authorUrl: subMatch ? `https://www.reddit.com/r/${subMatch[1]}/` : undefined,
      categories: ctx?.categories?.length ? ctx.categories : cat ? [cat] : ["lifestyle"],
      embed: { type: "oembed-html", html: embedHtml(canonicalUrl), scriptSrc: "https://embed.reddit.com/widgets.js" },
      origin: ctx?.origin ?? "user-submitted",
      fetchedAt: new Date().toISOString(),
    };
  },

  async feed(opts: FeedOptions) {
    if (!creds()) return [];
    const subs = (process.env.REDDIT_FEED_SUBREDDITS ?? "videos+funny+aww+science+gaming")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .join("+");
    const data = await api<{ data?: { children?: { data: RedditPost }[] } }>(`/r/${subs}/hot`, {
      limit: String(Math.min(opts.limit ?? 50, 100)),
    });
    return (data.data?.children ?? [])
      .map((c) => c.data)
      .filter((p) => !p.over_18)
      .map((p) => fromPost(p, "provider-api"))
      .filter((it) => !opts.categories?.length || it.categories.some((c) => opts.categories!.includes(c)));
  },

  async search(opts: SearchOptions) {
    if (!creds()) return [];
    const data = await api<{ data?: { children?: { data: RedditPost }[] } }>("/search", {
      q: opts.query,
      limit: String(Math.min(opts.limit ?? 12, 50)),
      sort: "relevance",
      type: "link",
      include_over_18: "off",
    });
    return (data.data?.children ?? []).map((c) => c.data).filter((p) => !p.over_18).map((p) => fromPost(p, "provider-api"));
  },
};
