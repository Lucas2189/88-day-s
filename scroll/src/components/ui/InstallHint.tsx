"use client";

import { Share, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { trackEvent } from "@/lib/analytics";
import { useT } from "@/lib/i18n";
import { useUserStore } from "@/lib/store/user-store";

/**
 * One-time hint explaining how to install the PWA. Shown only in a mobile browser tab (never when the
 * app already runs standalone), after onboarding, and never again once dismissed.
 */
export function InstallHint() {
  const dismissed = useUserStore((s) => s.preferences.installHintDismissed);
  const onboardingDone = useUserStore((s) => s.preferences.onboardingDone);
  const setPreferences = useUserStore((s) => s.setPreferences);
  const [platform, setPlatform] = useState<"ios" | "android" | null>(null);
  const t = useT();

  useEffect(() => {
    const timer = setTimeout(() => {
      const standalone = window.matchMedia("(display-mode: standalone)").matches || (navigator as Navigator & { standalone?: boolean }).standalone === true;
      if (standalone) return;
      const ua = navigator.userAgent;
      if (/iPhone|iPad|iPod/.test(ua)) setPlatform("ios");
      else if (/Android/.test(ua)) setPlatform("android");
    }, 8000);
    return () => clearTimeout(timer);
  }, []);

  const visible = platform !== null && onboardingDone && !dismissed;
  const dismiss = () => {
    setPreferences({ installHintDismissed: true });
    trackEvent("install_hint_dismissed");
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          role="status"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 16 }}
          className="fixed inset-x-3 z-[55] mx-auto flex max-w-[536px] items-start gap-3 rounded-2xl border border-line bg-surface-2/95 p-4 shadow-float backdrop-blur-xl"
          style={{ bottom: "calc(var(--tabbar-h) + var(--safe-bottom) + 12px)" }}
        >
          <span className="mt-0.5 rounded-full bg-white/10 p-2">
            <Share size={16} />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">{t("install.title")}</p>
            <p className="mt-0.5 text-xs text-fg-muted">{t(platform === "ios" ? "install.ios" : "install.android")}</p>
          </div>
          <button type="button" onClick={dismiss} aria-label={t("install.dismiss")} className="rounded-full p-1 text-fg-muted hover:text-fg">
            <X size={16} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
