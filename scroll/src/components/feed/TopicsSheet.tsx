"use client";

import { Chip } from "@/components/ui/Chip";
import { Sheet } from "@/components/ui/Sheet";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { CATEGORY_IDS, CATEGORY_LABELS, PROVIDER_IDS } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

export function TopicsSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const preferences = useUserStore((s) => s.preferences);
  const toggleInterest = useUserStore((s) => s.toggleInterest);
  const toggleProvider = useUserStore((s) => s.toggleProvider);
  const setPreferences = useUserStore((s) => s.setPreferences);

  return (
    <Sheet open={open} onClose={onClose} title="Tune your feed">
      <section>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Interests</h3>
        <p className="mt-1 text-sm text-fg-muted">Pick what you like. Leave empty to see everything.</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {CATEGORY_IDS.map((c) => (
            <Chip key={c} active={preferences.interests.includes(c)} onClick={() => toggleInterest(c)}>
              {CATEGORY_LABELS[c]}
            </Chip>
          ))}
        </div>
      </section>
      <section className="mt-6">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Sources</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {PROVIDER_IDS.map((p) => (
            <Chip key={p} active={preferences.enabledProviders.includes(p)} onClick={() => toggleProvider(p)}>
              {PROVIDER_NAMES[p]}
            </Chip>
          ))}
        </div>
      </section>
      <section className="mt-6">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Discovery</h3>
        <label className="mt-3 block text-sm text-fg-muted">
          Exploration: <span className="text-fg">{Math.round(preferences.exploration * 100)}%</span>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={preferences.exploration}
            onChange={(e) => setPreferences({ exploration: Number(e.target.value) })}
            className="mt-2 w-full accent-white"
            aria-label="Exploration level"
          />
          <span className="mt-1 block text-xs text-fg-faint">Higher = more variety between platforms and topics; lower = strictly what matches your interests.</span>
        </label>
      </section>
    </Sheet>
  );
}
