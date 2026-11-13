/**
 * Unified content model shared by every provider adapter.
 * Only metadata that providers expose through authorized endpoints (oEmbed,
 * official APIs) is stored here. Media files are never downloaded or stored.
 */

export const PROVIDER_IDS = ["youtube", "tiktok", "instagram", "x", "reddit"] as const;
export type ProviderId = (typeof PROVIDER_IDS)[number];

export const CATEGORY_IDS = [
  "music",
  "comedy",
  "gaming",
  "tech",
  "science",
  "sports",
  "food",
  "travel",
  "art",
  "animals",
  "news",
  "film",
  "education",
  "lifestyle",
] as const;
export type CategoryId = (typeof CATEGORY_IDS)[number];

export const CATEGORY_LABELS: Record<CategoryId, string> = {
  music: "Music",
  comedy: "Comedy",
  gaming: "Gaming",
  tech: "Tech",
  science: "Science",
  sports: "Sports",
  food: "Food",
  travel: "Travel",
  art: "Art & Design",
  animals: "Animals",
  news: "News",
  film: "Film & Animation",
  education: "Education",
  lifestyle: "Lifestyle",
};

export type ContentKind = "video" | "post" | "image" | "link";

/** How the item can be rendered inside SCROLL. */
export type EmbedStrategy =
  | { type: "youtube-player"; videoId: string }
  | { type: "tiktok-player"; videoId: string }
  | { type: "oembed-html"; html: string; scriptSrc?: string }
  | { type: "iframe"; src: string; aspectRatio?: number }
  | { type: "link-card" };

export type ContentOrigin = "demo" | "user-submitted" | "provider-api" | "curated";

export interface ContentItem {
  /** Stable internal id: `${provider}:${externalId}` */
  id: string;
  provider: ProviderId;
  externalId: string;
  kind: ContentKind;
  /** Canonical public URL of the original publication. */
  url: string;
  title: string;
  description?: string;
  authorName?: string;
  authorUrl?: string;
  thumbnailUrl?: string;
  thumbnailWidth?: number;
  thumbnailHeight?: number;
  /** Duration in seconds when the provider exposes it. */
  durationSeconds?: number;
  publishedAt?: string;
  categories: CategoryId[];
  tags?: string[];
  embed: EmbedStrategy;
  origin: ContentOrigin;
  /** ISO timestamp of when metadata was fetched; used for cache expiry and attribution. */
  fetchedAt: string;
  /** Provider-specific extras we are allowed to persist (e.g. YouTube statistics). */
  extras?: Record<string, string | number | boolean | null>;
}

export interface ProviderCapabilities {
  /** Can the adapter resolve a public URL into a ContentItem? */
  resolveUrl: boolean;
  /** Can the adapter produce a discovery feed without user-submitted URLs? */
  feed: boolean;
  /** Can the adapter search the provider catalog? */
  search: boolean;
  /** Can SCROLL autoplay the embedded media (muted) when it becomes active? */
  autoplay: boolean;
  /** Can SCROLL control mute/unmute programmatically? */
  muteControl: boolean;
  /** Whether the embed exposes playback progress to SCROLL. */
  progressEvents: boolean;
}

export type ProviderStatus =
  | { level: "live"; detail: string }
  | { level: "partial"; detail: string }
  | { level: "unavailable"; detail: string };

export interface ProviderInfo {
  id: ProviderId;
  name: string;
  /** Short brand color used for badges only (not a logo). */
  accent: string;
  capabilities: ProviderCapabilities;
  status: ProviderStatus;
  /** Which env vars unlock additional capabilities. */
  requiredEnv: string[];
  docsUrl: string;
}

export interface FeedResponse {
  items: ContentItem[];
  providers: ProviderInfo[];
  generatedAt: string;
  /** Explains how items were sourced so the UI can label them honestly. */
  notes: string[];
}

export interface ResolveResponse {
  item: ContentItem;
}

export interface ApiError {
  error: string;
  code: "invalid_url" | "unsupported_provider" | "not_found" | "provider_error" | "rate_limited" | "bad_request";
  provider?: ProviderId;
}
