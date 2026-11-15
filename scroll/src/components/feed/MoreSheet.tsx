"use client";

import { EyeOff, Flag, Info, Link2, UserX } from "lucide-react";
import { Sheet } from "@/components/ui/Sheet";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import type { ContentItem } from "@/lib/content/types";
import { useT, type MessageKey } from "@/lib/i18n";
import type { ReasonCode } from "@/lib/ranking/score";

interface Props {
  item: ContentItem | null;
  reasons: ReasonCode[];
  open: boolean;
  onClose: () => void;
  onHide: (alsoAuthor: boolean) => void;
  onCopyLink: () => void;
}

const ORIGIN_KEY: Record<ContentItem["origin"], MessageKey> = {
  demo: "more.origin.demo",
  "user-submitted": "more.origin.user",
  "provider-api": "more.origin.api",
  curated: "more.origin.curated",
};

export function MoreSheet({ item, reasons, open, onClose, onHide, onCopyLink }: Props) {
  const t = useT();
  if (!item) return null;
  const row = "flex w-full items-center gap-3 rounded-2xl border border-line bg-surface-2 px-4 py-3 text-left text-sm font-medium";
  return (
    <Sheet open={open} onClose={onClose} title={t("more.title")}>
      <div className="space-y-3">
        <div className="rounded-2xl border border-line bg-surface-2 p-4 text-sm">
          <p className="flex items-start gap-2 text-fg-muted">
            <Info size={16} className="mt-0.5 shrink-0" />
            <span>
              <strong className="text-fg">{t("more.platform", { platform: PROVIDER_NAMES[item.provider] })}</strong>
              {item.authorName ? <span className="block">{t("more.author", { author: item.authorName })}</span> : null}
              <span className="mt-1 block">{t(ORIGIN_KEY[item.origin])}</span>
            </span>
          </p>
          <p className="mt-2 text-xs text-fg-faint">{t("more.topics", { topics: item.categories.map((c) => t(`category.${c}`)).join(", ") })}</p>
          {reasons.length > 0 && <p className="mt-2 text-xs text-fg-faint">{t("more.why", { reasons: reasons.map((r) => t(`reason.${r}`)).join(" · ") })}</p>}
          <p className="mt-2 text-xs text-fg-faint">{t("more.noMedia")}</p>
        </div>
        <button type="button" className={row} onClick={onCopyLink}>
          <Link2 size={18} /> {t("more.copyLink")}
        </button>
        <button type="button" className={row} onClick={() => onHide(false)}>
          <EyeOff size={18} /> {t("more.hideThis")}
        </button>
        {item.authorName && (
          <button type="button" className={row} onClick={() => onHide(true)}>
            <UserX size={18} /> {t("more.lessFrom", { name: item.authorName })}
          </button>
        )}
        <a href={item.url} target="_blank" rel="noopener noreferrer" className={row}>
          <Flag size={18} /> {t("more.report", { platform: PROVIDER_NAMES[item.provider] })}
        </a>
      </div>
    </Sheet>
  );
}
