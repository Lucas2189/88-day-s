import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { ProviderLogo } from "@/components/ui/ProviderLogo";
import type { ProviderInfo } from "@/lib/content/types";

const LEVEL_STYLE = {
  live: "bg-emerald-500/15 text-emerald-200 border-emerald-400/30",
  partial: "bg-amber-500/15 text-amber-100 border-amber-400/30",
  unavailable: "bg-red-500/15 text-red-200 border-red-400/30",
} as const;

const LEVEL_LABEL = { live: "Live", partial: "Partial", unavailable: "Unavailable" } as const;

export function SourceStatusList({ providers }: { providers: ProviderInfo[] }) {
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
            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${LEVEL_STYLE[p.status.level]}`}>{LEVEL_LABEL[p.status.level]}</span>
          </div>
          <p className="mt-2 text-xs text-fg-muted">{p.status.detail}</p>
          <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
            <Cap ok={p.capabilities.resolveUrl} label="Paste link" />
            <Cap ok={p.capabilities.feed} label="Discovery feed" />
            <Cap ok={p.capabilities.search} label="Search" />
            <Cap ok={p.capabilities.autoplay} label="Autoplay" />
          </div>
        </li>
      ))}
    </ul>
  );
}

function Cap({ ok, label }: { ok: boolean; label: string }) {
  return <span className={`rounded-full border px-2 py-0.5 ${ok ? "border-white/15 text-fg" : "border-white/5 text-fg-faint line-through"}`}>{label}</span>;
}
