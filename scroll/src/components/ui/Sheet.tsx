"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";

interface SheetProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  /** Height hint; content scrolls inside. */
  tall?: boolean;
}

/** Bottom sheet with drag-to-dismiss, dark glass look, safe-area aware. */
export function Sheet({ open, onClose, title, children, tall }: SheetProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            aria-label="Close"
            className="fixed inset-0 z-[60] bg-black/60 backdrop-blur-[2px]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label={title}
            className={`fixed inset-x-0 bottom-0 z-[65] mx-auto flex w-full max-w-[560px] flex-col rounded-t-[28px] border-t border-line bg-surface shadow-float ${tall ? "h-[88dvh]" : "max-h-[82dvh]"}`}
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", stiffness: 380, damping: 38 }}
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.6 }}
            onDragEnd={(_, info) => {
              if (info.offset.y > 120 || info.velocity.y > 600) onClose();
            }}
          >
            <div className="flex items-center justify-between px-5 pb-2 pt-3">
              <div className="mx-auto h-1.5 w-10 rounded-full bg-white/20" />
            </div>
            {title && (
              <div className="flex items-center justify-between px-5 pb-3">
                <h2 className="font-display text-lg font-semibold">{title}</h2>
                <button onClick={onClose} className="rounded-full bg-surface-2 p-2 text-fg-muted hover:text-fg" aria-label="Close sheet">
                  <X size={18} />
                </button>
              </div>
            )}
            <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto px-5 pb-[calc(var(--safe-bottom)+20px)]">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
