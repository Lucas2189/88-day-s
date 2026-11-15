"use client";

import Link from "next/link";
import { useT, type MessageKey } from "@/lib/i18n";

/** Full-page localized message with a single action back to the feed. */
export function StatusScreen({ title, body, action }: { title: MessageKey; body?: MessageKey; action: MessageKey }) {
  const t = useT();
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">{t(title)}</p>
      {body && <p className="max-w-xs text-sm text-fg-muted">{t(body)}</p>}
      <Link href="/" className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
        {t(action)}
      </Link>
    </main>
  );
}
