"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useToast } from "@/components/ui/Toast";
import type { ContentItem } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";
import { EndSlide } from "./EndSlide";
import { FeedHeader } from "./FeedHeader";
import { FeedItem } from "./FeedItem";
import { FeedSkeleton } from "./FeedSkeleton";
import { MoreSheet } from "./MoreSheet";
import { OnboardingSheet } from "./OnboardingSheet";
import { SaveSheet } from "./SaveSheet";
import { TopicsSheet } from "./TopicsSheet";
import { useRankedFeed, type FeedScope } from "./useRankedFeed";

const SKIP_THRESHOLD_SECONDS = 2;

export function Feed({ scope, title, pinFirstId }: { scope: FeedScope; title?: string; pinFirstId?: string | null }) {
  const { ranked, isLoading, isError, error, refresh } = useRankedFeed(scope, { pinFirstId });
  const preferences = useUserStore((s) => s.preferences);
  const likes = useUserStore((s) => s.likes);
  const bookmarks = useUserStore((s) => s.bookmarks);
  const toggleLike = useUserStore((s) => s.toggleLike);
  const toggleBookmark = useUserStore((s) => s.toggleBookmark);
  const hideContent = useUserStore((s) => s.hideContent);
  const track = useUserStore((s) => s.track);
  const markSeen = useUserStore((s) => s.markSeen);
  const { toast } = useToast();
  const router = useRouter();

  const [activeIndex, setActiveIndex] = useState(0);
  const [saveTarget, setSaveTarget] = useState<ContentItem | null>(null);
  const [moreTarget, setMoreTarget] = useState<{ item: ContentItem; reasons: string[] } | null>(null);
  const [topicsOpen, setTopicsOpen] = useState(false);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const dwell = useRef<{ item: ContentItem; startedAt: number; completed: boolean } | null>(null);

  const items = useMemo(() => ranked.map((r) => r.item), [ranked]);

  // Engagement: close the dwell window for the previous item whenever the active item changes.
  const flushDwell = useCallback(
    (next: ContentItem | null) => {
      const prev = dwell.current;
      if (prev && prev.item.id !== next?.id) {
        const seconds = (Date.now() - prev.startedAt) / 1000;
        if (prev.completed) track(prev.item, "complete", seconds);
        else if (seconds < SKIP_THRESHOLD_SECONDS) track(prev.item, "skip", seconds);
        else track(prev.item, "view", seconds);
      }
      dwell.current = next ? { item: next, startedAt: Date.now(), completed: false } : null;
      if (next) markSeen(next.id);
    },
    [track, markSeen],
  );

  useEffect(() => {
    flushDwell(items[activeIndex] ?? null);
  }, [activeIndex, items, flushDwell]);

  useEffect(() => () => flushDwell(null), [flushDwell]);

  // IntersectionObserver picks the slide occupying the viewport.
  useEffect(() => {
    const root = scrollerRef.current;
    if (!root) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.6) {
            const idx = Number((entry.target as HTMLElement).dataset.index);
            if (!Number.isNaN(idx)) setActiveIndex(idx);
          }
        }
      },
      { root, threshold: [0.6] },
    );
    root.querySelectorAll<HTMLElement>("[data-index]").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [items.length]);

  // Keyboard navigation for desktop testing / accessibility.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const root = scrollerRef.current;
      if (!root) return;
      if (e.key === "ArrowDown" || e.key === "j") root.scrollBy({ top: root.clientHeight, behavior: "smooth" });
      if (e.key === "ArrowUp" || e.key === "k") root.scrollBy({ top: -root.clientHeight, behavior: "smooth" });
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const share = useCallback(
    async (item: ContentItem) => {
      track(item, "share");
      try {
        if (navigator.share) {
          await navigator.share({ title: item.title, url: item.url });
          return;
        }
        await navigator.clipboard.writeText(item.url);
        toast("Link copied", "success");
      } catch {
        /* user cancelled */
      }
    },
    [track, toast],
  );

  const open = useCallback(
    (item: ContentItem) => {
      track(item, "open");
      window.open(item.url, "_blank", "noopener,noreferrer");
    },
    [track],
  );

  const hide = useCallback(
    (item: ContentItem, alsoAuthor = false) => {
      hideContent(item, alsoAuthor);
      setMoreTarget(null);
      toast(alsoAuthor ? `You'll see less from ${item.authorName}` : "Hidden from your feed");
    },
    [hideContent, toast],
  );

  if (isLoading) return <FeedSkeleton />;

  if (isError) {
    return (
      <div className="flex min-h-dvh flex-col items-center justify-center gap-3 px-8 text-center">
        <p className="font-display text-xl font-semibold">Couldn&apos;t load the feed</p>
        <p className="text-sm text-fg-muted">{error?.message ?? "Please check your connection and try again."}</p>
        <button type="button" onClick={refresh} className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
          Retry
        </button>
      </div>
    );
  }

  return (
    <>
      <FeedHeader onRefresh={() => { refresh(); scrollerRef.current?.scrollTo({ top: 0 }); toast("Feed refreshed"); }} onOpenTopics={() => setTopicsOpen(true)} title={title} />
      <div ref={scrollerRef} className="feed-scroller" role="feed" aria-busy={isLoading}>
        {items.map((item, index) => (
          <FeedItem
            key={item.id}
            item={item}
            index={index}
            active={index === activeIndex}
            near={Math.abs(index - activeIndex) <= 1}
            autoplay={preferences.autoplay}
            startMuted={preferences.startMuted}
            liked={Boolean(likes[item.id])}
            saved={Boolean(bookmarks[item.id])}
            onLike={() => {
              const liked = toggleLike(item);
              if (liked) toast("Liked");
            }}
            onSave={() => {
              if (bookmarks[item.id]) {
                setSaveTarget(item);
              } else {
                toggleBookmark(item);
                toast("Saved · tap again to pick a collection", "success");
              }
            }}
            onShare={() => share(item)}
            onHide={() => hide(item)}
            onOpen={() => open(item)}
            onMore={() => setMoreTarget({ item, reasons: ranked[index]?.reasons ?? [] })}
            onEnded={() => {
              if (dwell.current?.item.id === item.id) dwell.current.completed = true;
            }}
            onPlay={() => undefined}
          />
        ))}
        <EndSlide
          count={items.length}
          onRefresh={() => {
            if (scope.kind === "home") refresh();
            else router.push("/");
            scrollerRef.current?.scrollTo({ top: 0, behavior: "smooth" });
          }}
        />
      </div>

      <SaveSheet item={saveTarget} open={saveTarget !== null} onClose={() => setSaveTarget(null)} />
      <MoreSheet
        item={moreTarget?.item ?? null}
        reasons={moreTarget?.reasons ?? []}
        open={moreTarget !== null}
        onClose={() => setMoreTarget(null)}
        onHide={(alsoAuthor) => moreTarget && hide(moreTarget.item, alsoAuthor)}
        onCopyLink={async () => {
          if (!moreTarget) return;
          await navigator.clipboard.writeText(moreTarget.item.url);
          toast("Link copied", "success");
        }}
      />
      <TopicsSheet open={topicsOpen} onClose={() => setTopicsOpen(false)} />
      {scope.kind === "home" && <OnboardingSheet />}
    </>
  );
}
