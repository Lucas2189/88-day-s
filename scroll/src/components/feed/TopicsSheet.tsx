"use client";

import { Chip } from "@/components/ui/Chip";
import { Sheet } from "@/components/ui/Sheet";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { CATEGORY_IDS, PROVIDER_IDS } from "@/lib/content/types";
import { useT } from "@/lib/i18n";
import { useUserStore } from "@/lib/store/user-store";

export function TopicsSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const preferences = useUserStore((s) => s.preferences);
  const toggleInterest = useUserStore((s) => s.toggleInterest);
  const toggleProvider = useUserStore((s) => s.toggleProvider);
  const setPreferences = useUserStore((s) => s.setPreferences);
  const t = useT();

  return (
    <Sheet open={open} onClose={onClose} title={t("topics.title")}>
      <section>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">{t("topics.interests")}</h3>
        <p className="mt-1 text-sm text-fg-muted">{t("topics.interestsHint")}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {CATEGORY_IDS.map((c) => (
            <Chip key={c} active={preferences.interests.includes(c)} onClick={() => toggleInterest(c)}>
              {t(`category.${c}`)}
            </Chip>
          ))}
        </div>
      </section>
      <section className="mt-6">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">{t("topics.sources")}</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {PROVIDER_IDS.map((p) => (
            <Chip key={p} active={preferences.enabledProviders.includes(p)} onClick={() => toggleProvider(p)}>
              {PROVIDER_NAMES[p]}
            </Chip>
          ))}
        </div>
      </section>
      <section className="mt-6">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">{t("topics.discovery")}</h3>
        <label className="mt-3 block text-sm text-fg-muted">
          <span className="text-fg">{t("topics.exploration", { percent: Math.round(preferences.exploration * 100) })}</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={preferences.exploration}
            onChange={(e) => setPreferences({ exploration: Number(e.target.value) })}
            className="mt-2 w-full accent-white"
            aria-label={t("topics.discovery")}
          />
          <span className="mt-1 block text-xs text-fg-faint">{t("topics.explorationHint")}</span>
        </label>
      </section>
    </Sheet>
  );
}
