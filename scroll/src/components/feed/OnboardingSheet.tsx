"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Sheet } from "@/components/ui/Sheet";
import { CATEGORY_IDS, CATEGORY_LABELS } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

/** First-run interest picker. Shown once; skippable. */
export function OnboardingSheet() {
  const onboardingDone = useUserStore((s) => s.preferences.onboardingDone);
  const interests = useUserStore((s) => s.preferences.interests);
  const toggleInterest = useUserStore((s) => s.toggleInterest);
  const setPreferences = useUserStore((s) => s.setPreferences);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    // Wait for persisted state to hydrate before deciding.
    const t = setTimeout(() => setOpen(!useUserStore.getState().preferences.onboardingDone), 400);
    return () => clearTimeout(t);
  }, []);

  if (onboardingDone) return null;
  const finish = () => {
    setPreferences({ onboardingDone: true });
    setOpen(false);
  };

  return (
    <Sheet open={open} onClose={finish} title="Welcome to SCROLL">
      <p className="text-sm text-fg-muted">One feed, every network. Pick a few topics to start, or skip and let your scrolling shape the feed.</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {CATEGORY_IDS.map((c) => (
          <Chip key={c} active={interests.includes(c)} onClick={() => toggleInterest(c)}>
            {CATEGORY_LABELS[c]}
          </Chip>
        ))}
      </div>
      <div className="mt-6 flex gap-2">
        <Button className="flex-1" onClick={finish}>
          {interests.length ? `Start with ${interests.length} topic${interests.length > 1 ? "s" : ""}` : "Start scrolling"}
        </Button>
      </div>
      <p className="mt-4 text-xs text-fg-faint">Content plays through each platform&apos;s official embed. Your signals (views, saves, skips) stay on this device unless you sign in to sync.</p>
    </Sheet>
  );
}
