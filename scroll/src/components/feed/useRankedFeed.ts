"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "@/lib/api/client";
import type { ContentItem } from "@/lib/content/types";
import { learnAffinity, rankItems, type ScoredItem } from "@/lib/ranking/score";
import { selectRankingProfile, useUserStore } from "@/lib/store/user-store";

export type FeedScope = { kind: "home" } | { kind: "saved"; collectionId?: string } | { kind: "items"; items: ContentItem[] };

/**
 * Loads the candidate pool and ranks it with the user's private signals. The order is frozen until the
 * pool, filters or an explicit refresh change, so the feed never reshuffles under the user's thumb.
 */
export function useRankedFeed(scope: FeedScope, opts: { pinFirstId?: string | null } = {}) {
  const preferences = useUserStore((s) => s.preferences);
  const submitted = useUserStore((s) => s.submitted);
  const bookmarks = useUserStore((s) => s.bookmarks);
  const hiddenContentIds = useUserStore((s) => s.hiddenContentIds);
  const hiddenAuthors = useUserStore((s) => s.hiddenAuthors);
  const sessionSeed = useUserStore((s) => s.sessionSeed);
  const [refreshToken, setRefreshToken] = useState(0);

  const providers = preferences.feedMode === "mixed" ? preferences.enabledProviders : [preferences.feedMode];

  const query = useQuery({
    queryKey: ["feed", providers.slice().sort().join(","), preferences.interests.slice().sort().join(","), refreshToken],
    queryFn: () => api.feed({ providers }),
    enabled: scope.kind === "home",
    staleTime: 5 * 60_000,
  });

  const pool: ContentItem[] = useMemo(() => {
    if (scope.kind === "items") return scope.items;
    if (scope.kind === "saved") {
      return Object.values(bookmarks)
        .filter((b) => !scope.collectionId || b.collectionIds.includes(scope.collectionId))
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
        .map((b) => b.item);
    }
    const remote = query.data?.items ?? [];
    const local = Object.values(submitted);
    const seen = new Set<string>();
    return [...local, ...remote].filter((it) => (seen.has(it.id) ? false : (seen.add(it.id), true)));
  }, [scope, query.data, submitted, bookmarks]);

  // Affinity is learned from a snapshot of events taken when the pool changes or on refresh,
  // not on every engagement, so the order stays stable while the user scrolls.
  const affinity = useMemo(
    () => learnAffinity(useUserStore.getState().events),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [pool, refreshToken],
  );

  const ranked: ScoredItem[] = useMemo(() => {
    const state = useUserStore.getState();
    const profile = selectRankingProfile({ ...state, preferences, hiddenContentIds, hiddenAuthors, sessionSeed }, affinity);
    if (scope.kind !== "home") {
      // Saved/explicit lists keep their own order; only hidden filtering applies.
      return pool
        .filter((it) => !profile.hiddenContentIds.has(it.id))
        .map((item) => ({ item, score: 0, reasons: [] }));
    }
    // Seen penalty is applied only on refresh; during a session the order stays frozen.
    const frozenProfile = { ...profile, seenContentIds: new Set<string>() };
    const result = rankItems(pool, frozenProfile, { diversify: preferences.exploration > 0.25 });
    if (opts.pinFirstId) {
      const idx = result.findIndex((r) => r.item.id === opts.pinFirstId);
      if (idx > 0) {
        const [pinned] = result.splice(idx, 1);
        result.unshift(pinned);
      }
    }
    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pool, affinity, preferences, hiddenContentIds, hiddenAuthors, sessionSeed, scope.kind, refreshToken, opts.pinFirstId]);

  return {
    ranked,
    isLoading: scope.kind === "home" && query.isLoading,
    isError: scope.kind === "home" && query.isError,
    error: query.error as Error | null,
    notes: query.data?.notes ?? [],
    providersInfo: query.data?.providers ?? [],
    refresh: () => {
      useUserStore.getState().resetSession();
      setRefreshToken((t) => t + 1);
      void query.refetch();
    },
  };
}
