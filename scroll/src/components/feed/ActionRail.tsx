"use client";

import clsx from "clsx";
import { Bookmark, EyeOff, Heart, MoreHorizontal, Share2, Volume2, VolumeX, ExternalLink } from "lucide-react";
import { motion } from "motion/react";
import type { ReactNode } from "react";

interface RailButtonProps {
  label: string;
  icon: ReactNode;
  onClick: () => void;
  active?: boolean;
  activeClass?: string;
  count?: string;
}

function RailButton({ label, icon, onClick, active, activeClass, count }: RailButtonProps) {
  return (
    <motion.button
      type="button"
      whileTap={{ scale: 0.86 }}
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      className="flex w-14 flex-col items-center gap-0.5 text-fg"
    >
      <span className={clsx("flex h-10 w-10 items-center justify-center rounded-full bg-white/[0.08] backdrop-blur-md transition-colors", active && activeClass)}>{icon}</span>
      <span className="text-[10px] font-medium text-fg-muted">{count ?? label}</span>
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
  return (
    <div className="flex shrink-0 flex-col items-center justify-end gap-2 self-stretch pb-1">
      {p.canToggleSound && (
        <RailButton label={p.muted ? "Unmute" : "Mute"} icon={p.muted ? <VolumeX size={18} /> : <Volume2 size={18} />} onClick={p.onToggleSound} />
      )}
      <RailButton
        label="Like"
        icon={<Heart size={18} fill={p.liked ? "currentColor" : "none"} />}
        onClick={p.onLike}
        active={p.liked}
        activeClass="bg-like/20 text-like"
      />
      <RailButton
        label="Save"
        icon={<Bookmark size={18} fill={p.saved ? "currentColor" : "none"} />}
        onClick={p.onSave}
        active={p.saved}
        activeClass="bg-save/20 text-save"
      />
      <RailButton label="Share" icon={<Share2 size={18} />} onClick={p.onShare} />
      <RailButton label="Open" icon={<ExternalLink size={18} />} onClick={p.onOpen} />
      <RailButton label="Hide" icon={<EyeOff size={18} />} onClick={p.onHide} />
      <RailButton label="More" icon={<MoreHorizontal size={18} />} onClick={p.onMore} />
    </div>
  );
}
