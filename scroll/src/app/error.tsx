"use client";

import { useEffect } from "react";

export default function ErrorBoundary({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("[app] route error", error);
  }, [error]);
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">Something went wrong</p>
      <p className="max-w-xs text-sm text-fg-muted">{error.message || "An unexpected error occurred."}</p>
      <button type="button" onClick={reset} className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
        Try again
      </button>
    </main>
  );
}
