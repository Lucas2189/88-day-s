"use client";

import clsx from "clsx";
import { Play } from "lucide-react";
import { motion } from "motion/react";
import { memo, useCallback, useEffect, useRef, useState } from "react";
import { EmbedRenderer } from "@/components/embeds/EmbedRenderer";
import type { PlayerHandle } from "@/components/embeds/types";
import { ProviderBadge } from "@/components/ui/ProviderBadge";
import { SmartImage } from "@/components/ui/SmartImage";
import { CATEGORY_LABELS, type ContentItem } from "@/lib/content/types";
import { ActionRail } from "./ActionRail";

export interface FeedItemProps {
  item: ContentItem;
  index: number;
  active: boolean;
  /** Pre-render the poster of neighbours so swipes feel instant. */
  near: boolean;
  autoplay: boolean;
  startMuted: boolean;
  liked: boolean;
  saved: boolean;
  onLike: () => void;
  onSave: () => void;
  onShare: () => void;
  onHide: () => void;
  onOpen: () => void;
  onMore: () => void;
  onEnded: () => void;
  onPlay: () => void;
}

const SUPPORTS_SOUND = new Set(["youtube-player", "tiktok-player"]);

/** Media box aspect by embed type: players get a fixed ratio, rich embeds scroll inside a tall card. */
function mediaShape(item: ContentItem): { ratio: number | null } {
  if (item.embed.type === "youtube-player") return { ratio: 16 / 9 };
  if (item.embed.type === "tiktok-player") return { ratio: 9 / 16 };
  return { ratio: null };
}

export const FeedItem = memo(function FeedItem(p: FeedItemProps) {
  const playerRef = useRef<PlayerHandle>(null);
  const [muted, setMuted] = useState(p.startMuted);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const canToggleSound = SUPPORTS_SOUND.has(p.item.embed.type);
  const { ratio } = mediaShape(p.item);

  // Reset transient playback state when the slide leaves the viewport (state-from-props pattern).
  const [prevActive, setPrevActive] = useState(p.active);
  if (prevActive !== p.active) {
    setPrevActive(p.active);
    if (!p.active) {
      setReady(false);
      setError(null);
      setMuted(p.startMuted);
    }
  }

  const toggleSound = useCallback(() => {
    if (muted) playerRef.current?.unmute();
    else playerRef.current?.mute();
    setMuted((m) => !m);
  }, [muted]);

  const showEmbed = p.active && !error;

  return (
    <article className="feed-slide flex flex-col bg-black" aria-label={p.item.title} data-index={p.index}>
      {/* Header spacer (filter bar is fixed above) */}
      <div className="shrink-0" style={{ height: "calc(var(--safe-top) + 56px)" }} />

      {/* Media region + action rail: the rail sits BESIDE the player so nothing overlays third-party UI */}
      <div className="flex min-h-0 flex-1 items-center gap-1 px-2">
        <div className="relative flex h-full min-w-0 flex-1 items-center justify-center">
          <div
            className={clsx("relative w-full overflow-hidden rounded-2xl bg-surface", ratio === null && "h-full")}
            style={ratio ? { aspectRatio: String(ratio), maxHeight: "100%", ...(ratio < 1 ? { width: "auto", height: "100%" } : {}) } : undefined}
          >
            {/* Poster (always rendered for active/near so swipes are instant) */}
            {(p.near || p.active) && (
              <Poster item={p.item} visible={!showEmbed || !ready} />
            )}
            {showEmbed && (
              <div className={clsx("absolute inset-0 transition-opacity duration-300", ready ? "opacity-100" : "opacity-0")}>
                <EmbedRenderer
                  ref={playerRef}
                  item={p.item}
                  autoplay={p.autoplay}
                  startMuted={p.startMuted}
                  onReady={() => setReady(true)}
                  onPlay={() => {
                    setReady(true);
                    p.onPlay();
                  }}
                  onEnded={p.onEnded}
                  onMuteChange={setMuted}
                  onError={(msg) => setError(msg)}
                />
              </div>
            )}
            {showEmbed && p.item.embed.type === "oembed-html" && !ready && (
              <ReadyWatcher onReady={() => setReady(true)} />
            )}
            {error && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/80 p-6 text-center">
                <p className="text-sm text-fg-muted">{error}</p>
                <a href={p.item.url} target="_blank" rel="noopener noreferrer" className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-black">
                  Watch on the original platform
                </a>
              </div>
            )}
          </div>
        </div>
        <ActionRail
          liked={p.liked}
          saved={p.saved}
          muted={muted}
          canToggleSound={canToggleSound && p.active}
          onLike={p.onLike}
          onSave={p.onSave}
          onShare={p.onShare}
          onHide={p.onHide}
          onOpen={p.onOpen}
          onToggleSound={toggleSound}
          onMore={p.onMore}
        />
      </div>

      {/* Info bar */}
      <div className="shrink-0 px-4 pt-3" style={{ paddingBottom: "calc(var(--tabbar-h) + var(--safe-bottom) + 12px)" }}>
        <div className="flex items-center gap-2">
          <ProviderBadge provider={p.item.provider} />
          {p.item.origin === "demo" && (
            <span className="rounded-full border border-white/10 bg-white/[0.06] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-fg-muted">Demo</span>
          )}
          {p.item.origin === "user-submitted" && (
            <span className="rounded-full border border-white/10 bg-white/[0.06] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-fg-muted">Your link</span>
          )}
        </div>
        <h2 className="mt-2 line-clamp-2 font-display text-[17px] font-semibold leading-snug">{p.item.title}</h2>
        <p className="mt-1 line-clamp-1 text-sm text-fg-muted">
          {p.item.authorName ?? "Unknown author"}
          <span className="text-fg-faint"> · {p.item.categories.map((c) => CATEGORY_LABELS[c]).join(" · ")}</span>
        </p>
      </div>
    </article>
  );
});

function Poster({ item, visible }: { item: ContentItem; visible: boolean }) {
  return (
    <motion.div
      className="absolute inset-0 flex items-center justify-center bg-surface"
      initial={false}
      animate={{ opacity: visible ? 1 : 0 }}
      transition={{ duration: 0.25 }}
      style={{ pointerEvents: visible ? "auto" : "none" }}
    >
      {item.thumbnailUrl ? (
        <SmartImage src={item.thumbnailUrl} className="h-full w-full object-cover opacity-80" />
      ) : (
        <div className="flex h-full w-full flex-col items-center justify-center gap-3 p-6 text-center">
          <p className="line-clamp-4 text-base text-fg-muted">{item.description ?? item.title}</p>
        </div>
      )}
      {item.kind === "video" && (
        <span className="absolute flex h-14 w-14 items-center justify-center rounded-full bg-black/55 backdrop-blur-md">
          <Play size={24} fill="currentColor" />
        </span>
      )}
    </motion.div>
  );
}

/** Rich oEmbed widgets don't emit a ready event; reveal them after a short grace period. */
function ReadyWatcher({ onReady }: { onReady: () => void }) {
  useEffect(() => {
    const t = setTimeout(onReady, 900);
    return () => clearTimeout(t);
  }, [onReady]);
  return null;
}
