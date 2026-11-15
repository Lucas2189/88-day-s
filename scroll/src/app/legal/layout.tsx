import { ChevronLeft } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

/** Shared shell for the legal pages. They are written in English, the reference language for legal terms. */
export default function LegalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh px-5 pb-16" style={{ paddingTop: "calc(var(--safe-top) + 16px)" }}>
      <Link href="/profile" className="inline-flex items-center gap-1 rounded-full bg-white/[0.08] py-2 pl-2 pr-4 text-sm font-medium">
        <ChevronLeft size={18} /> SCROLL
      </Link>
      <article className="legal mt-6 space-y-4 text-[15px] leading-relaxed text-fg-muted">{children}</article>
    </div>
  );
}
