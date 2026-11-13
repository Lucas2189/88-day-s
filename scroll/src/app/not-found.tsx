import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-4 px-8 text-center">
      <p className="font-display text-2xl font-semibold">Page not found</p>
      <Link href="/" className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
        Back to feed
      </Link>
    </main>
  );
}
