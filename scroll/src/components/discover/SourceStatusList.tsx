"use client";

import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { ProviderLogo } from "@/components/ui/ProviderLogo";
import type { ProviderInfo } from "@/lib/content/types";
import { useT, type MessageKey } from "@/lib/i18n";

const LEVEL_STYLE = {
  live: "bg-emerald-500/15 text-emerald-200 border-emerald-400/30",
  partial: "bg-amber-500/15 text-amber-100 border-amber-400/30",
  unavailable: "bg-red-500/15 text-red-200 border-red-400/30",
} as const;

/** Localized description of what each provider supports, derived from its id and status level. */
function detailKey(p: ProviderInfo): MessageKey {
  if (p.id === "youtube") return p.status.level === "live" ? "source.detail.youtube.live" : "source.detail.youtube.partial";
  if (p.id === "reddit") return p.status.level === "live" ? "source.detail.reddit.live" : "source.detail.reddit.partial";
  return `source.detail.${p.id}`;
}

export function SourceStatusList({ providers }: { providers: ProviderInfo[] }) {
  const t = useT();
  if (!providers.length) return <div className="skeleton mt-3 h-24 rounded-2xl" />;
  return (
    <ul className="mt-3 space-y-2">
      {providers.map((p) => (
        <li key={p.id} className="rounded-2xl border border-line bg-surface-2 p-4">
          <div className="flex items-center justify-between gap-3">
            <span className="flex items-center gap-2 text-sm font-semibold">
              <ProviderLogo provider={p.id} size={16} />
              {PROVIDER_NAMES[p.id]}
            </span>
            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${LEVEL_STYLE[p.status.level]}`}>{t(`source.level.${p.status.level}`)}</span>
          </div>
          <p className="mt-2 text-xs text-fg-muted">{t(detailKey(p))}</p>
          <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
            <Cap ok={p.capabilities.resolveUrl} label={t("source.cap.paste")} />
            <Cap ok={p.capabilities.feed} label={t("source.cap.feed")} />
            <Cap ok={p.capabilities.search} label={t("source.cap.search")} />
            <Cap ok={p.capabilities.autoplay} label={t("source.cap.autoplay")} />
          </div>
        </li>
      ))}
    </ul>
  );
}

function Cap({ ok, label }: { ok: boolean; label: string }) {
  return <span className={`rounded-full border px-2 py-0.5 ${ok ? "border-white/15 text-fg" : "border-white/5 text-fg-faint line-through"}`}>{label}</span>;
}
