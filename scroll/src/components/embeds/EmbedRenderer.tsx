"use client";

import { forwardRef } from "react";
import type { ContentItem } from "@/lib/content/types";
import { OEmbedHtml } from "./OEmbedHtml";
import { TikTokPlayer } from "./TikTokPlayer";
import { YouTubePlayer } from "./YouTubePlayer";
import type { PlayerEvents, PlayerHandle } from "./types";
import { ExternalLink } from "lucide-react";

interface Props extends PlayerEvents {
  item: ContentItem;
  autoplay: boolean;
  startMuted: boolean;
}

/** Picks the right official embed for an item. Unknown strategies fall back to a link card. */
export const EmbedRenderer = forwardRef<PlayerHandle, Props>(function EmbedRenderer({ item, autoplay, startMuted, ...events }, ref) {
  const { embed } = item;
  switch (embed.type) {
    case "youtube-player":
      return <YouTubePlayer ref={ref} videoId={embed.videoId} autoplay={autoplay} startMuted={startMuted} {...events} />;
    case "tiktok-player":
      return <TikTokPlayer ref={ref} videoId={embed.videoId} autoplay={autoplay} startMuted={startMuted} {...events} />;
    case "oembed-html":
      return <OEmbedHtml html={embed.html} scriptSrc={embed.scriptSrc} onError={events.onError} />;
    case "iframe":
      return (
        <div className="embed-shell h-full w-full">
          <iframe title={item.title} src={embed.src} allow="autoplay; encrypted-media; fullscreen; picture-in-picture" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" />
        </div>
      );
    default:
      return (
        <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex h-full w-full flex-col items-center justify-center gap-3 p-6 text-center">
          <ExternalLink size={28} className="text-fg-muted" />
          <p className="text-sm text-fg-muted">This content can only be viewed on the original platform.</p>
          <span className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-black">Open original</span>
        </a>
      );
  }
});
