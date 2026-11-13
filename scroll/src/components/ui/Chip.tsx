"use client";

import clsx from "clsx";
import type { ButtonHTMLAttributes } from "react";

interface ChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
  size?: "sm" | "md";
}

export function Chip({ active, size = "md", className, children, ...rest }: ChipProps) {
  return (
    <button
      type="button"
      aria-pressed={active}
      className={clsx(
        "shrink-0 select-none rounded-full border font-medium transition-colors active:scale-[0.97]",
        size === "sm" ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm",
        active ? "border-white bg-white text-black" : "border-line bg-white/[0.06] text-fg-muted hover:bg-white/[0.1] hover:text-fg",
        className,
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
