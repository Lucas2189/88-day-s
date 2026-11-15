"use client";

import clsx from "clsx";
import { Bookmark, EyeOff, Heart, MoreHorizontal, Share2, Volume2, VolumeX, ExternalLink } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";
import { useT } from "@/lib/i18n";

interface RailButtonProps {
  /** Stable identifier for tests and analytics, independent of the UI language. */
  action: string;
  label: string;
  icon: ReactNode;
  onClick: () => void;
  active?: boolean;
  activeClass?: string;
  count?: string;
}

function RailButton({ action, label, icon, onClick, active, activeClass, count }: RailButtonProps) {
  return (
    <motion.button
      type="button"
      whileTap={{ scale: 0.86 }}
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      data-action={action}
      className="flex w-14 flex-col items-center gap-0.5 text-fg"
    >
      <span className={clsx("flex h-10 w-10 items-center justify-center rounded-full bg-white/[0.08] backdrop-blur-md transition-colors", active && activeClass)}>{icon}</span>
      <span className="max-w-14 truncate text-[10px] font-medium text-fg-muted">{count ?? label}</span>
    </motion.button>
  );
}

interface ActionRailProps {
  liked: boolean;
  saved: boolean;
  muted: boolean;
  canToggleSound: boolean;
  onLike: () => void;
  onSave: () => void;
  onShare: () => void;
  onHide: () => void;
  onOpen: () => void;
  onToggleSound: () => void;
  onMore: () => void;
}

export function ActionRail(p: ActionRailProps) {
  const t = useT();
  return (
    <div className="flex shrink-0 flex-col items-center justify-end gap-2 self-stretch pb-1">
      {p.canToggleSound && (
        <RailButton action="sound" label={p.muted ? t("action.unmute") : t("action.mute")} icon={p.muted ? <VolumeX size={18} /> : <Volume2 size={18} />} onClick={p.onToggleSound} />
      )}
      <RailButton
        action="like"
        label={t("action.like")}
        icon={<Heart size={18} fill={p.liked ? "currentColor" : "none"} />}
        onClick={p.onLike}
        active={p.liked}
        activeClass="bg-like/20 text-like"
      />
      <RailButton
        action="save"
        label={t("action.save")}
        icon={<Bookmark size={18} fill={p.saved ? "currentColor" : "none"} />}
        onClick={p.onSave}
        active={p.saved}
        activeClass="bg-save/20 text-save"
      />
      <RailButton action="share" label={t("action.share")} icon={<Share2 size={18} />} onClick={p.onShare} />
      <RailButton action="open" label={t("action.open")} icon={<ExternalLink size={18} />} onClick={p.onOpen} />
      <RailButton action="hide" label={t("action.hide")} icon={<EyeOff size={18} />} onClick={p.onHide} />
      <RailButton action="more" label={t("action.more")} icon={<MoreHorizontal size={18} />} onClick={p.onMore} />
    </div>
  );
}
