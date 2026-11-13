"use client";

import { Play } from "lucide-react";
import { ProviderBadge } from "@/components/ui/ProviderBadge";
import { SmartImage } from "@/components/ui/SmartImage";
import type { ContentItem } from "@/lib/content/types";

export function ContentCard({ item, onOpen }: { item: ContentItem; onOpen: () => void }) {
  return (
    <button type="button" onClick={onOpen} className="group relative aspect-[3/4] overflow-hidden rounded-2xl bg-surface-2 text-left">
      {item.thumbnailUrl ? (
        <SmartImage src={item.thumbnailUrl} cropLetterbox className="h-full w-full object-cover transition-transform duration-500" />
      ) : (
        <div className="flex h-full w-full items-center justify-center p-4 text-center text-sm text-fg-muted">{item.description ?? item.title}</div>
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
      <ProviderBadge provider={item.provider} compact className="absolute left-2 top-2" />
      {item.kind === "video" && <Play size={16} fill="currentColor" className="absolute right-2 top-2 text-white drop-shadow" />}
      <div className="absolute inset-x-0 bottom-0 p-3">
        <p className="line-clamp-2 text-sm font-semibold leading-tight">{item.title}</p>
        <p className="mt-1 line-clamp-1 text-[11px] text-fg-muted">{item.authorName}</p>
      </div>
    </button>
  );
}
