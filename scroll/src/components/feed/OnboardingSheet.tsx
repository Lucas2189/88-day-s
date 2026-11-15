"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Sheet } from "@/components/ui/Sheet";
import { CATEGORY_IDS } from "@/lib/content/types";
import { useT } from "@/lib/i18n";
import { trackEvent } from "@/lib/analytics";
import { useUserStore } from "@/lib/store/user-store";

/** First-run interest picker. Shown once; skippable. */
export function OnboardingSheet() {
  const onboardingDone = useUserStore((s) => s.preferences.onboardingDone);
  const interests = useUserStore((s) => s.preferences.interests);
  const toggleInterest = useUserStore((s) => s.toggleInterest);
  const setPreferences = useUserStore((s) => s.setPreferences);
  const [open, setOpen] = useState(false);
  const t = useT();

  useEffect(() => {
    // Wait for persisted state to hydrate before deciding.
    const t = setTimeout(() => setOpen(!useUserStore.getState().preferences.onboardingDone), 400);
    return () => clearTimeout(t);
  }, []);

  if (onboardingDone) return null;
  const finish = () => {
    setPreferences({ onboardingDone: true });
    trackEvent("onboarding_done", { topics: interests.length });
    setOpen(false);
  };

  return (
    <Sheet open={open} onClose={finish} title={t("onboarding.title")}>
      <p className="text-sm text-fg-muted">{t("onboarding.body")}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {CATEGORY_IDS.map((c) => (
          <Chip key={c} active={interests.includes(c)} onClick={() => toggleInterest(c)}>
            {t(`category.${c}`)}
          </Chip>
        ))}
      </div>
      <div className="mt-6 flex gap-2">
        <Button className="flex-1" data-testid="onboarding-start" onClick={finish}>
          {interests.length ? t("onboarding.startSelected", { count: interests.length }) : t("onboarding.start")}
        </Button>
      </div>
      <p className="mt-4 text-xs text-fg-faint">{t("onboarding.privacy")}</p>
    </Sheet>
  );
}
