"use client";

import { RefreshCw, SlidersHorizontal } from "lucide-react";
import { Chip } from "@/components/ui/Chip";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { ProviderLogo } from "@/components/ui/ProviderLogo";
import type { ProviderId } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

interface Props {
  onRefresh: () => void;
  onOpenTopics: () => void;
  title?: string;
}

/** Fixed translucent bar: feed mode (mixed / per-platform) + topic sheet + refresh. */
export function FeedHeader({ onRefresh, onOpenTopics, title }: Props) {
  const preferences = useUserStore((s) => s.preferences);
  const setPreferences = useUserStore((s) => s.setPreferences);
  const enabled = preferences.enabledProviders;

  return (
    <div className="fixed inset-x-0 top-0 z-40 mx-auto w-full max-w-[560px] bg-gradient-to-b from-black via-black/85 to-transparent pb-4" style={{ paddingTop: "var(--safe-top)" }}>
      <div className="flex h-14 items-center gap-2 px-3">
        {title ? (
          <h1 className="font-display text-lg font-semibold">{title}</h1>
        ) : (
          <div className="no-scrollbar flex min-w-0 flex-1 items-center gap-2 overflow-x-auto">
            <Chip size="sm" active={preferences.feedMode === "mixed"} onClick={() => setPreferences({ feedMode: "mixed" })}>
              For you
            </Chip>
            {enabled.map((id: ProviderId) => (
              <Chip key={id} size="sm" active={preferences.feedMode === id} onClick={() => setPreferences({ feedMode: id })} className="flex items-center gap-1.5">
                <ProviderLogo provider={id} size={12} />
                {PROVIDER_NAMES[id]}
              </Chip>
            ))}
          </div>
        )}
        <div className="ml-auto flex shrink-0 items-center gap-1">
          <button type="button" onClick={onOpenTopics} aria-label="Topics" className="rounded-full bg-white/[0.08] p-2 text-fg backdrop-blur-md hover:bg-white/[0.14]">
            <SlidersHorizontal size={18} />
          </button>
          <button type="button" onClick={onRefresh} aria-label="Refresh feed" className="rounded-full bg-white/[0.08] p-2 text-fg backdrop-blur-md hover:bg-white/[0.14]">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
