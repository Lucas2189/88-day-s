"use client";

import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    instgrm?: { Embeds: { process: () => void } };
    twttr?: { widgets: { load: (el?: HTMLElement) => Promise<void> } };
  }
}

const loadedScripts = new Map<string, Promise<void>>();

function loadScript(src: string): Promise<void> {
  const existing = loadedScripts.get(src);
  if (existing) return existing;
  const p = new Promise<void>((resolve, reject) => {
    const s = document.createElement("script");
    s.src = src;
    s.async = true;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.body.appendChild(s);
  });
  loadedScripts.set(src, p);
  return p;
}

/** Strips any inline/external <script> so only the provider loader we control runs. */
function stripScripts(html: string): string {
  return html.replace(/<script[\s\S]*?<\/script>/gi, "");
}

/**
 * Renders official oEmbed HTML (X, Instagram, Reddit) and boots the provider's embed script.
 * The provider script is loaded once; subsequent embeds are processed in place.
 */
export function OEmbedHtml({ html, scriptSrc, onError }: { html: string; scriptSrc?: string; onError?: (message: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let cancelled = false;
    el.innerHTML = stripScripts(html);

    const boot = async () => {
      if (!scriptSrc) {
        setStatus("ready");
        return;
      }
      try {
        if (scriptSrc.includes("embed.reddit.com")) {
          // Reddit's loader scans blockquotes when executed; re-execute per embed.
          await new Promise<void>((resolve, reject) => {
            const s = document.createElement("script");
            s.src = scriptSrc;
            s.async = true;
            s.onload = () => resolve();
            s.onerror = () => reject(new Error("reddit loader failed"));
            el.appendChild(s);
          });
        } else {
          await loadScript(scriptSrc);
          if (scriptSrc.includes("instagram.com")) window.instgrm?.Embeds.process();
          if (scriptSrc.includes("platform.twitter.com")) await window.twttr?.widgets.load(el);
        }
        if (!cancelled) setStatus("ready");
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          onError?.((err as Error).message);
        }
      }
    };
    void boot();
    return () => {
      cancelled = true;
      el.innerHTML = "";
    };
  }, [html, scriptSrc, onError]);

  return (
    <div className="relative h-full w-full overflow-y-auto overscroll-contain no-scrollbar">
      {status === "loading" && <div className="skeleton absolute inset-0 rounded-2xl" aria-hidden />}
      <div ref={ref} className="embed-shell relative mx-auto flex min-h-full w-full max-w-[540px] items-center justify-center px-2 py-2" />
    </div>
  );
}
