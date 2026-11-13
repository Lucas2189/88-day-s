import clsx from "clsx";
import type { ProviderId } from "@/lib/content/types";
import { ProviderLogo } from "./ProviderLogo";

export const PROVIDER_NAMES: Record<ProviderId, string> = {
  youtube: "YouTube",
  tiktok: "TikTok",
  instagram: "Instagram",
  x: "X",
  reddit: "Reddit",
};

/** Small pill identifying the original platform. Always visible on every feed item. */
export function ProviderBadge({ provider, className, compact }: { provider: ProviderId; className?: string; compact?: boolean }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-black/55 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-white backdrop-blur-md",
        className,
      )}
      title={`Original platform: ${PROVIDER_NAMES[provider]}`}
    >
      <ProviderLogo provider={provider} size={12} />
      {!compact && PROVIDER_NAMES[provider]}
    </span>
  );
}
