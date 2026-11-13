import Link from "next/link";

export const metadata = { title: "Offline" };

export default function OfflinePage() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">You&apos;re offline</p>
      <p className="max-w-xs text-sm text-fg-muted">SCROLL needs a connection to load content from the platforms. Your saved items and preferences are safe on this device.</p>
      <Link href="/" className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
        Try again
      </Link>
    </main>
  );
}
