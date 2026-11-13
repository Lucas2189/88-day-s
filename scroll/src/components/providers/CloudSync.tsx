"use client";

import type { Session } from "@supabase/supabase-js";
import { useEffect, useRef } from "react";
import { getSupabaseBrowserClient } from "@/lib/supabase/client";
import { mergeSnapshots, pullSnapshot, pushEvents, pushSnapshot } from "@/lib/supabase/sync";
import { useUserStore } from "@/lib/store/user-store";
import type { EngagementEvent } from "@/lib/ranking/score";

/**
 * Keeps local state and Supabase in sync when the user is signed in. Mounted once in AppProviders.
 * Does nothing in local-only mode.
 */
export function CloudSync() {
  const sessionRef = useRef<Session | null>(null);
  const pendingEvents = useRef<EngagementEvent[]>([]);
  const pushTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const sb = getSupabaseBrowserClient();
    if (!sb) return;

    const schedulePush = () => {
      if (pushTimer.current) clearTimeout(pushTimer.current);
      pushTimer.current = setTimeout(async () => {
        const session = sessionRef.current;
        if (!session) return;
        try {
          await pushSnapshot(sb, session.user.id, useUserStore.getState());
          const batch = pendingEvents.current.splice(0, pendingEvents.current.length);
          await pushEvents(sb, session.user.id, batch);
        } catch (err) {
          console.warn("[sync] push failed", err);
        }
      }, 1500);
    };

    const onEngagement = (e: Event) => {
      pendingEvents.current.push((e as CustomEvent<EngagementEvent>).detail);
      schedulePush();
    };
    window.addEventListener("scroll:engagement", onEngagement);

    const unsubStore = useUserStore.subscribe((state, prev) => {
      if (
        state.preferences !== prev.preferences ||
        state.bookmarks !== prev.bookmarks ||
        state.collections !== prev.collections ||
        state.hiddenContentIds !== prev.hiddenContentIds ||
        state.hiddenAuthors !== prev.hiddenAuthors
      ) {
        schedulePush();
      }
    });

    const { data: auth } = sb.auth.onAuthStateChange(async (_event, session) => {
      const wasSignedIn = Boolean(sessionRef.current);
      sessionRef.current = session;
      if (session && !wasSignedIn) {
        try {
          const remote = await pullSnapshot(sb, session.user.id);
          const merged = mergeSnapshots(useUserStore.getState(), remote);
          useUserStore.getState().hydrateFrom(merged);
          await pushSnapshot(sb, session.user.id, useUserStore.getState());
        } catch (err) {
          console.warn("[sync] initial sync failed", err);
        }
      }
    });

    return () => {
      window.removeEventListener("scroll:engagement", onEngagement);
      unsubStore();
      auth.subscription.unsubscribe();
      if (pushTimer.current) clearTimeout(pushTimer.current);
    };
  }, []);

  return null;
}
