"use client";

import { useEffect } from "react";
import { useT } from "@/lib/i18n";

export default function ErrorBoundary({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const t = useT();
  useEffect(() => {
    console.error("[app] route error", error);
  }, [error]);
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">{t("errorPage.title")}</p>
      <button type="button" onClick={reset} className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
        {t("common.retry")}
      </button>
    </main>
  );
}
