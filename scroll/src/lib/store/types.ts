import type { CategoryId, ContentItem, ProviderId } from "@/lib/content/types";
import type { EngagementEvent } from "@/lib/ranking/score";
import type { LocalePreference, RegionPreference } from "@/lib/i18n/locales";

export type FeedMode = "mixed" | ProviderId;

export interface Preferences {
  interests: CategoryId[];
  enabledProviders: ProviderId[];
  feedMode: FeedMode;
  autoplay: boolean;
  startMuted: boolean;
  /** 0 = pure relevance, 1 = maximum exploration/diversity. */
  exploration: number;
  reducedMotion: boolean;
  onboardingDone: boolean;
  /** UI language: "auto" follows the browser. */
  locale: LocalePreference;
  /** Content region used to boost local content: "auto" follows the browser/locale. */
  region: RegionPreference;
  /** Set when the user dismissed the install hint. */
  installHintDismissed: boolean;
}

export interface Bookmark {
  contentId: string;
  item: ContentItem;
  collectionIds: string[];
  note?: string;
  createdAt: string;
}

export interface Collection {
  id: string;
  name: string;
  emoji?: string;
  createdAt: string;
}

export interface UserState {
  preferences: Preferences;
  bookmarks: Record<string, Bookmark>;
  collections: Record<string, Collection>;
  likes: Record<string, string>; // contentId -> createdAt
  hiddenContentIds: Record<string, string>;
  hiddenAuthors: Record<string, string>;
  /** User-submitted items persist locally so they come back in the feed. */
  submitted: Record<string, ContentItem>;
  events: EngagementEvent[];
  seenContentIds: Record<string, string>;
  sessionSeed: number;
}

export const DEFAULT_PREFERENCES: Preferences = {
  interests: [],
  enabledProviders: ["youtube", "tiktok", "instagram", "x", "reddit"],
  feedMode: "mixed",
  autoplay: true,
  startMuted: true,
  exploration: 0.4,
  reducedMotion: false,
  onboardingDone: false,
  locale: "auto",
  region: "auto",
  installHintDismissed: false,
};
