"use client";

import { Link2, RefreshCw } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { useT } from "@/lib/i18n";

export function EndSlide({ onRefresh, count }: { onRefresh: () => void; count: number }) {
  const t = useT();
  return (
    <section className="feed-slide flex flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">{t("feed.endTitle")}</p>
      <p className="max-w-xs text-sm text-fg-muted">
        {count > 0 ? t("feed.endCount", { count }) : t("feed.endEmpty")} {t("feed.endHint")}
      </p>
      <div className="flex gap-2">
        <Button onClick={onRefresh}>
          <RefreshCw size={16} /> {t("feed.refresh")}
        </Button>
        <Link href="/discover?add=1" className="inline-flex h-11 items-center gap-2 rounded-full border border-line bg-white/[0.08] px-5 text-sm font-semibold">
          <Link2 size={16} /> {t("feed.addLink")}
        </Link>
      </div>
    </section>
  );
}
