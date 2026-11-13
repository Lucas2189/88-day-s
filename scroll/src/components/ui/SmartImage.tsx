"use client";

import clsx from "clsx";
import { useState } from "react";

/**
 * Thumbnail with graceful fallback. For YouTube we try the higher-resolution variants first and fall back to
 * the oEmbed-provided one (which always exists). YouTube's sd/hq thumbnails are 4:3 with letterbox bars, so
 * `cropLetterbox` scales them up slightly to hide the bars in portrait cards.
 */
export function SmartImage({ src, alt = "", className, cropLetterbox }: { src: string; alt?: string; className?: string; cropLetterbox?: boolean }) {
  const isYt = src.includes("i.ytimg.com") && src.includes("hqdefault");
  const candidates = isYt ? [src.replace("hqdefault", "maxresdefault"), src.replace("hqdefault", "sddefault"), src] : [src];
  const [idx, setIdx] = useState(0);
  const safeIdx = Math.min(idx, candidates.length - 1);
  const current = candidates[safeIdx];
  const letterboxed = isYt && safeIdx > 0 && cropLetterbox;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={current}
      alt={alt}
      className={clsx(className, letterboxed && "scale-[1.34]")}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onLoad={(e) => {
        // YouTube serves a 120x90 placeholder instead of 404 for missing sizes.
        if (e.currentTarget.naturalWidth <= 120 && safeIdx < candidates.length - 1) setIdx(safeIdx + 1);
      }}
      onError={() => safeIdx < candidates.length - 1 && setIdx(safeIdx + 1)}
    />
  );
}
