"use client";

import type { SupabaseClient, Session } from "@supabase/supabase-js";
import type { UserState } from "@/lib/store/types";
import type { EngagementEvent } from "@/lib/ranking/score";
import type { Bookmark, Collection } from "@/lib/store/types";

/**
 * Cloud persistence (optional). Local state is the source of truth for the device; when a session exists we
 * merge the remote snapshot on login and push changes afterwards. Conflict rule: union for bookmarks /
 * collections / hidden sets; the most recent `updated_at` wins for preferences.
 */

export async function pullSnapshot(sb: SupabaseClient, userId: string): Promise<Partial<UserState>> {
  const [prefs, bookmarks, collections, hidden] = await Promise.all([
    sb.from("user_preferences").select("preferences").eq("user_id", userId).maybeSingle(),
    sb.from("bookmarks").select("content_id, item, collection_ids, note, created_at").eq("user_id", userId),
    sb.from("collections").select("id, name, emoji, created_at").eq("user_id", userId),
    sb.from("hidden_content").select("target, target_type, created_at").eq("user_id", userId),
  ]);

  const snapshot: Partial<UserState> = {};
  if (prefs.data?.preferences) snapshot.preferences = prefs.data.preferences as UserState["preferences"];
  if (bookmarks.data) {
    const map: Record<string, Bookmark> = {};
    for (const b of bookmarks.data) {
      map[b.content_id] = { contentId: b.content_id, item: b.item, collectionIds: b.collection_ids ?? [], note: b.note ?? undefined, createdAt: b.created_at };
    }
    snapshot.bookmarks = map;
  }
  if (collections.data) {
    const map: Record<string, Collection> = {};
    for (const c of collections.data) map[c.id] = { id: c.id, name: c.name, emoji: c.emoji ?? undefined, createdAt: c.created_at };
    snapshot.collections = map;
  }
  if (hidden.data) {
    snapshot.hiddenContentIds = {};
    snapshot.hiddenAuthors = {};
    for (const h of hidden.data) {
      if (h.target_type === "content") snapshot.hiddenContentIds[h.target] = h.created_at;
      else snapshot.hiddenAuthors[h.target] = h.created_at;
    }
  }
  return snapshot;
}

export function mergeSnapshots(local: UserState, remote: Partial<UserState>): Partial<UserState> {
  return {
    preferences: remote.preferences ?? local.preferences,
    bookmarks: { ...(remote.bookmarks ?? {}), ...local.bookmarks },
    collections: { ...(remote.collections ?? {}), ...local.collections },
    hiddenContentIds: { ...(remote.hiddenContentIds ?? {}), ...local.hiddenContentIds },
    hiddenAuthors: { ...(remote.hiddenAuthors ?? {}), ...local.hiddenAuthors },
  };
}

export async function pushSnapshot(sb: SupabaseClient, userId: string, state: UserState): Promise<void> {
  await sb.from("user_preferences").upsert({ user_id: userId, preferences: state.preferences, updated_at: new Date().toISOString() });

  const collections = Object.values(state.collections).map((c) => ({ id: c.id, user_id: userId, name: c.name, emoji: c.emoji ?? null, created_at: c.createdAt }));
  if (collections.length) await sb.from("collections").upsert(collections);

  const bookmarks = Object.values(state.bookmarks).map((b) => ({
    user_id: userId,
    content_id: b.contentId,
    item: b.item,
    collection_ids: b.collectionIds,
    note: b.note ?? null,
    created_at: b.createdAt,
  }));
  if (bookmarks.length) await sb.from("bookmarks").upsert(bookmarks, { onConflict: "user_id,content_id" });

  const remoteBookmarks = await sb.from("bookmarks").select("content_id").eq("user_id", userId);
  const localIds = new Set(Object.keys(state.bookmarks));
  const stale = (remoteBookmarks.data ?? []).map((r) => r.content_id).filter((id) => !localIds.has(id));
  if (stale.length) await sb.from("bookmarks").delete().eq("user_id", userId).in("content_id", stale);

  const hidden = [
    ...Object.entries(state.hiddenContentIds).map(([target, created_at]) => ({ user_id: userId, target, target_type: "content", created_at })),
    ...Object.entries(state.hiddenAuthors).map(([target, created_at]) => ({ user_id: userId, target, target_type: "author", created_at })),
  ];
  if (hidden.length) await sb.from("hidden_content").upsert(hidden, { onConflict: "user_id,target_type,target" });
}

export async function pushEvents(sb: SupabaseClient, userId: string, events: EngagementEvent[]): Promise<void> {
  if (!events.length) return;
  await sb.from("engagement_events").upsert(
    events.map((e) => ({
      id: e.id,
      user_id: userId,
      content_id: e.contentId,
      provider: e.provider,
      categories: e.categories,
      author_key: e.authorKey ?? null,
      event_type: e.type,
      dwell_seconds: e.dwellSeconds ?? null,
      created_at: e.createdAt,
    })),
    { onConflict: "id", ignoreDuplicates: true },
  );
}

export type { Session };
