"use client";

import clsx from "clsx";
import { Bookmark, Compass, Home, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useT, type MessageKey } from "@/lib/i18n";

const TABS = [
  { href: "/", label: "nav.home", icon: Home },
  { href: "/discover", label: "nav.discover", icon: Compass },
  { href: "/saved", label: "nav.saved", icon: Bookmark },
  { href: "/profile", label: "nav.profile", icon: UserRound },
] as const satisfies readonly { href: string; label: MessageKey; icon: typeof Home }[];

export function TabBar() {
  const pathname = usePathname();
  const t = useT();
  if (pathname.startsWith("/auth") || pathname === "/offline" || pathname.startsWith("/legal")) return null;
  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-50 mx-auto w-full max-w-[560px] border-t border-line bg-black/80 backdrop-blur-xl"
      style={{ paddingBottom: "var(--safe-bottom)" }}
    >
      <ul className="grid h-[var(--tabbar-h)] grid-cols-4">
        {TABS.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <li key={href}>
              <Link
                href={href}
                aria-current={active ? "page" : undefined}
                className={clsx(
                  "flex h-full flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors",
                  active ? "text-white" : "text-fg-faint hover:text-fg-muted",
                )}
              >
                <Icon size={22} strokeWidth={active ? 2.4 : 1.8} />
                {t(label)}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
