"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { CategoryId, ContentItem, ProviderId } from "@/lib/content/types";
import type { EngagementEvent, EngagementType } from "@/lib/ranking/score";
import { DEFAULT_PREFERENCES, type Bookmark, type Collection, type Preferences, type UserState } from "./types";

const MAX_EVENTS = 2000;

function uid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

export interface UserActions {
  setPreferences: (patch: Partial<Preferences>) => void;
  toggleInterest: (category: CategoryId) => void;
  toggleProvider: (provider: ProviderId) => void;
  toggleLike: (item: ContentItem) => boolean;
  toggleBookmark: (item: ContentItem, collectionId?: string) => boolean;
  setBookmarkCollections: (contentId: string, collectionIds: string[]) => void;
  createCollection: (name: string, emoji?: string) => Collection;
  renameCollection: (id: string, name: string) => void;
  deleteCollection: (id: string) => void;
  hideContent: (item: ContentItem, alsoAuthor?: boolean) => void;
  unhideAll: () => void;
  addSubmitted: (item: ContentItem) => void;
  removeSubmitted: (contentId: string) => void;
  track: (item: ContentItem, type: EngagementType, dwellSeconds?: number) => void;
  markSeen: (contentId: string) => void;
  resetSession: () => void;
  clearAll: () => void;
  /** Replaces local state with a snapshot (used by cloud sync). */
  hydrateFrom: (snapshot: Partial<UserState>) => void;
}

export type UserStore = UserState & UserActions;

const initialState = (): UserState => ({
  preferences: DEFAULT_PREFERENCES,
  bookmarks: {},
  collections: {},
  likes: {},
  hiddenContentIds: {},
  hiddenAuthors: {},
  submitted: {},
  events: [],
  seenContentIds: {},
  sessionSeed: Math.floor(Math.random() * 1_000_000),
});

export const authorKeyOf = (item: ContentItem) => item.authorUrl ?? item.authorName;

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      ...initialState(),

      setPreferences: (patch) => set((s) => ({ preferences: { ...s.preferences, ...patch } })),

      toggleInterest: (category) =>
        set((s) => {
          const has = s.preferences.interests.includes(category);
          const interests = has ? s.preferences.interests.filter((c) => c !== category) : [...s.preferences.interests, category];
          return { preferences: { ...s.preferences, interests } };
        }),

      toggleProvider: (provider) =>
        set((s) => {
          const has = s.preferences.enabledProviders.includes(provider);
          const enabledProviders = has
            ? s.preferences.enabledProviders.filter((p) => p !== provider)
            : [...s.preferences.enabledProviders, provider];
          const feedMode = !has || s.preferences.feedMode !== provider ? s.preferences.feedMode : "mixed";
          return { preferences: { ...s.preferences, enabledProviders, feedMode } };
        }),

      toggleLike: (item) => {
        const liked = Boolean(get().likes[item.id]);
        set((s) => {
          const likes = { ...s.likes };
          if (liked) delete likes[item.id];
          else likes[item.id] = new Date().toISOString();
          return { likes };
        });
        get().track(item, liked ? "unlike" : "like");
        return !liked;
      },

      toggleBookmark: (item, collectionId) => {
        const existing = get().bookmarks[item.id];
        if (existing && !collectionId) {
          set((s) => {
            const bookmarks = { ...s.bookmarks };
            delete bookmarks[item.id];
            return { bookmarks };
          });
          get().track(item, "unsave");
          return false;
        }
        const bookmark: Bookmark = existing
          ? { ...existing, collectionIds: Array.from(new Set([...existing.collectionIds, ...(collectionId ? [collectionId] : [])])) }
          : { contentId: item.id, item, collectionIds: collectionId ? [collectionId] : [], createdAt: new Date().toISOString() };
        set((s) => ({ bookmarks: { ...s.bookmarks, [item.id]: bookmark } }));
        if (!existing) get().track(item, "save");
        return true;
      },

      setBookmarkCollections: (contentId, collectionIds) =>
        set((s) => {
          const b = s.bookmarks[contentId];
          if (!b) return {};
          return { bookmarks: { ...s.bookmarks, [contentId]: { ...b, collectionIds } } };
        }),

      createCollection: (name, emoji) => {
        const collection: Collection = { id: uid(), name: name.trim() || "Untitled", emoji, createdAt: new Date().toISOString() };
        set((s) => ({ collections: { ...s.collections, [collection.id]: collection } }));
        return collection;
      },

      renameCollection: (id, name) =>
        set((s) => (s.collections[id] ? { collections: { ...s.collections, [id]: { ...s.collections[id], name } } } : {})),

      deleteCollection: (id) =>
        set((s) => {
          const collections = { ...s.collections };
          delete collections[id];
          const bookmarks: Record<string, Bookmark> = {};
          for (const [k, b] of Object.entries(s.bookmarks)) bookmarks[k] = { ...b, collectionIds: b.collectionIds.filter((c) => c !== id) };
          return { collections, bookmarks };
        }),

      hideContent: (item, alsoAuthor = false) => {
        set((s) => {
          const hiddenContentIds = { ...s.hiddenContentIds, [item.id]: new Date().toISOString() };
          const hiddenAuthors = { ...s.hiddenAuthors };
          const key = authorKeyOf(item);
          if (alsoAuthor && key) hiddenAuthors[key] = new Date().toISOString();
          return { hiddenContentIds, hiddenAuthors };
        });
        get().track(item, "hide");
      },

      unhideAll: () => set({ hiddenContentIds: {}, hiddenAuthors: {} }),

      addSubmitted: (item) => set((s) => ({ submitted: { ...s.submitted, [item.id]: { ...item, origin: "user-submitted" } } })),
      removeSubmitted: (contentId) =>
        set((s) => {
          const submitted = { ...s.submitted };
          delete submitted[contentId];
          return { submitted };
        }),

      track: (item, type, dwellSeconds) => {
        const ev: EngagementEvent = {
          id: uid(),
          contentId: item.id,
          provider: item.provider,
          categories: item.categories,
          authorKey: authorKeyOf(item),
          type,
          dwellSeconds,
          createdAt: new Date().toISOString(),
        };
        set((s) => ({ events: [...s.events.slice(-(MAX_EVENTS - 1)), ev] }));
        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent("scroll:engagement", { detail: ev }));
        }
      },

      markSeen: (contentId) =>
        set((s) => (s.seenContentIds[contentId] ? {} : { seenContentIds: { ...s.seenContentIds, [contentId]: new Date().toISOString() } })),

      resetSession: () => set({ seenContentIds: {}, sessionSeed: Math.floor(Math.random() * 1_000_000) }),

      clearAll: () => set({ ...initialState(), preferences: { ...DEFAULT_PREFERENCES, onboardingDone: true } }),

      hydrateFrom: (snapshot) => set((s) => ({ ...s, ...snapshot })),
    }),
    {
      name: "scroll:user:v1",
      version: 1,
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({
        preferences: s.preferences,
        bookmarks: s.bookmarks,
        collections: s.collections,
        likes: s.likes,
        hiddenContentIds: s.hiddenContentIds,
        hiddenAuthors: s.hiddenAuthors,
        submitted: s.submitted,
        events: s.events,
        // seenContentIds and sessionSeed intentionally not persisted: they are per-session.
      }),
    },
  ),
);

/** Derives a RankingProfile from the store; memoized by callers via useMemo. */
export function selectRankingProfile(s: UserState, affinity: Partial<Record<CategoryId, number>>) {
  return {
    interests: s.preferences.interests,
    enabledProviders: s.preferences.feedMode === "mixed" ? s.preferences.enabledProviders : [s.preferences.feedMode],
    hiddenContentIds: new Set(Object.keys(s.hiddenContentIds)),
    hiddenAuthors: new Set(Object.keys(s.hiddenAuthors)),
    affinity,
    seenContentIds: new Set(Object.keys(s.seenContentIds)),
    skippedContentIds: new Set(s.events.filter((e) => e.type === "skip").map((e) => e.contentId)),
    seed: s.sessionSeed,
  };
}
