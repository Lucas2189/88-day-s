"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import type { PlayerEvents, PlayerHandle } from "./types";

/**
 * Official YouTube IFrame Player API. We never overlay UI on top of the player (YouTube API ToS) and
 * autoplay starts muted, with unmute only on a user gesture. Progress/completion events come from the API.
 */

interface YTPlayer {
  playVideo: () => void;
  pauseVideo: () => void;
  mute: () => void;
  unMute: () => void;
  isMuted: () => boolean;
  destroy: () => void;
}
interface YTNamespace {
  Player: new (
    el: HTMLElement,
    opts: {
      videoId: string;
      host?: string;
      playerVars?: Record<string, string | number>;
      events?: {
        onReady?: (e: { target: YTPlayer }) => void;
        onStateChange?: (e: { data: number; target: YTPlayer }) => void;
        onError?: (e: { data: number }) => void;
      };
    },
  ) => YTPlayer;
  PlayerState: { ENDED: number; PLAYING: number; PAUSED: number };
}

declare global {
  interface Window {
    YT?: YTNamespace;
    onYouTubeIframeAPIReady?: () => void;
    __ytApiPromise?: Promise<YTNamespace>;
  }
}

function loadYouTubeApi(): Promise<YTNamespace> {
  if (window.YT?.Player) return Promise.resolve(window.YT);
  if (window.__ytApiPromise) return window.__ytApiPromise;
  window.__ytApiPromise = new Promise<YTNamespace>((resolve) => {
    const previous = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      previous?.();
      resolve(window.YT!);
    };
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;
    document.head.appendChild(script);
  });
  return window.__ytApiPromise;
}

interface Props extends PlayerEvents {
  videoId: string;
  autoplay: boolean;
  startMuted: boolean;
}

export const YouTubePlayer = forwardRef<PlayerHandle, Props>(function YouTubePlayer(
  { videoId, autoplay, startMuted, onReady, onPlay, onEnded, onError, onMuteChange },
  ref,
) {
  const hostRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<YTPlayer | null>(null);
  const eventsRef = useRef({ onReady, onPlay, onEnded, onError, onMuteChange });
  eventsRef.current = { onReady, onPlay, onEnded, onError, onMuteChange };

  useImperativeHandle(ref, () => ({
    play: () => playerRef.current?.playVideo(),
    pause: () => playerRef.current?.pauseVideo(),
    mute: () => {
      playerRef.current?.mute();
      eventsRef.current.onMuteChange?.(true);
    },
    unmute: () => {
      playerRef.current?.unMute();
      eventsRef.current.onMuteChange?.(false);
    },
  }));

  useEffect(() => {
    let cancelled = false;
    const host = hostRef.current;
    if (!host) return;
    const mount = document.createElement("div");
    host.appendChild(mount);

    loadYouTubeApi().then((YT) => {
      if (cancelled) return;
      playerRef.current = new YT.Player(mount, {
        videoId,
        host: "https://www.youtube-nocookie.com",
        playerVars: {
          autoplay: autoplay ? 1 : 0,
          mute: startMuted ? 1 : 0,
          playsinline: 1,
          rel: 0,
          controls: 1,
          fs: 1,
          iv_load_policy: 3,
          enablejsapi: 1,
          origin: window.location.origin,
        },
        events: {
          onReady: (e) => {
            eventsRef.current.onReady?.();
            if (autoplay) e.target.playVideo();
          },
          onStateChange: (e) => {
            if (e.data === YT.PlayerState.PLAYING) eventsRef.current.onPlay?.();
            if (e.data === YT.PlayerState.ENDED) eventsRef.current.onEnded?.();
          },
          onError: (e) => {
            const reasons: Record<number, string> = {
              2: "Invalid video id.",
              5: "This video cannot be played in the embedded player.",
              100: "Video not found or private.",
              101: "The owner does not allow embedded playback.",
              150: "The owner does not allow embedded playback.",
            };
            eventsRef.current.onError?.(reasons[e.data] ?? "Playback error.");
          },
        },
      });
    });

    return () => {
      cancelled = true;
      try {
        playerRef.current?.destroy();
      } catch {
        /* ignore */
      }
      playerRef.current = null;
      mount.remove();
    };
  }, [videoId, autoplay, startMuted]);

  return <div ref={hostRef} className="embed-shell h-full w-full bg-black" />;
});
