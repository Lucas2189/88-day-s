"use client";

import { EyeOff, Flag, Info, Link2, UserX } from "lucide-react";
import { Sheet } from "@/components/ui/Sheet";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import type { ContentItem } from "@/lib/content/types";
import { CATEGORY_LABELS } from "@/lib/content/types";

interface Props {
  item: ContentItem | null;
  reasons: string[];
  open: boolean;
  onClose: () => void;
  onHide: (alsoAuthor: boolean) => void;
  onCopyLink: () => void;
}

const ORIGIN_LABEL: Record<ContentItem["origin"], string> = {
  demo: "Demo item: a real public publication, pre-selected to showcase the feed.",
  "user-submitted": "Added from a link you submitted.",
  "provider-api": "Fetched from the platform's official API.",
  curated: "Curated by SCROLL.",
};

export function MoreSheet({ item, reasons, open, onClose, onHide, onCopyLink }: Props) {
  if (!item) return null;
  const row = "flex w-full items-center gap-3 rounded-2xl border border-line bg-surface-2 px-4 py-3 text-left text-sm font-medium";
  return (
    <Sheet open={open} onClose={onClose} title="About this content">
      <div className="space-y-3">
        <div className="rounded-2xl border border-line bg-surface-2 p-4 text-sm">
          <p className="flex items-start gap-2 text-fg-muted">
            <Info size={16} className="mt-0.5 shrink-0" />
            <span>
              From <strong className="text-fg">{PROVIDER_NAMES[item.provider]}</strong>
              {item.authorName ? (
                <>
                  {" "}
                  by <strong className="text-fg">{item.authorName}</strong>
                </>
              ) : null}
              . {ORIGIN_LABEL[item.origin]}
            </span>
          </p>
          <p className="mt-2 text-xs text-fg-faint">Topics: {item.categories.map((c) => CATEGORY_LABELS[c]).join(", ")}</p>
          {reasons.length > 0 && <p className="mt-2 text-xs text-fg-faint">Why you see it: {reasons.join(" · ")}</p>}
          <p className="mt-2 text-xs text-fg-faint">Playback and metadata come from the platform&apos;s official embed. SCROLL does not store any media.</p>
        </div>
        <button type="button" className={row} onClick={onCopyLink}>
          <Link2 size={18} /> Copy original link
        </button>
        <button type="button" className={row} onClick={() => onHide(false)}>
          <EyeOff size={18} /> Hide this content
        </button>
        {item.authorName && (
          <button type="button" className={row} onClick={() => onHide(true)}>
            <UserX size={18} /> See less from {item.authorName}
          </button>
        )}
        <a href={item.url} target="_blank" rel="noopener noreferrer" className={row}>
          <Flag size={18} /> Report on {PROVIDER_NAMES[item.provider]}
        </a>
      </div>
    </Sheet>
  );
}
