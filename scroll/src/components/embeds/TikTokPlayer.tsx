"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import type { PlayerEvents, PlayerHandle } from "./types";

/**
 * TikTok Embed Player (https://developers.tiktok.com/doc/embed-player). The player renders TikTok's own
 * controls; SCROLL only sends the documented postMessage commands and listens to its events.
 */
interface Props extends PlayerEvents {
  videoId: string;
  autoplay: boolean;
  startMuted: boolean;
}

interface TikTokMessage {
  "x-tiktok-player"?: boolean;
  type?: string;
  value?: unknown;
}

export const TikTokPlayer = forwardRef<PlayerHandle, Props>(function TikTokPlayer(
  { videoId, autoplay, startMuted, onReady, onPlay, onEnded, onError, onMuteChange },
  ref,
) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [loaded, setLoaded] = useState(false);
  const eventsRef = useRef({ onReady, onPlay, onEnded, onError, onMuteChange });
  eventsRef.current = { onReady, onPlay, onEnded, onError, onMuteChange };

  const send = (type: string, value?: unknown) => {
    iframeRef.current?.contentWindow?.postMessage({ type, value, "x-tiktok-player": true }, "https://www.tiktok.com");
  };

  useImperativeHandle(ref, () => ({
    play: () => send("play"),
    pause: () => send("pause"),
    mute: () => {
      send("mute");
      eventsRef.current.onMuteChange?.(true);
    },
    unmute: () => {
      send("unMute");
      eventsRef.current.onMuteChange?.(false);
    },
  }));

  useEffect(() => {
    const onMessage = (event: MessageEvent<TikTokMessage>) => {
      if (event.origin !== "https://www.tiktok.com") return;
      if (event.source !== iframeRef.current?.contentWindow) return;
      const data = event.data;
      if (!data || !data["x-tiktok-player"]) return;
      switch (data.type) {
        case "onPlayerReady":
          eventsRef.current.onReady?.();
          break;
        case "onStateChange":
          if (data.value === 1) eventsRef.current.onPlay?.();
          if (data.value === 0) eventsRef.current.onEnded?.();
          break;
        case "onMute":
          eventsRef.current.onMuteChange?.(Boolean(data.value));
          break;
        case "onError":
          eventsRef.current.onError?.("TikTok player error.");
          break;
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  const params = new URLSearchParams({
    autoplay: autoplay ? "1" : "0",
    muted: startMuted ? "1" : "0",
    loop: "1",
    controls: "1",
    progress_bar: "1",
    play_button: "1",
    volume_control: "1",
    fullscreen_button: "1",
    timestamp: "0",
    music_info: "1",
    description: "1",
    rel: "0",
    native_context_menu: "1",
    closed_caption: "1",
  });

  return (
    <div className="embed-shell relative h-full w-full bg-black">
      {!loaded && <div className="skeleton absolute inset-0" aria-hidden />}
      <iframe
        ref={iframeRef}
        title={`TikTok video ${videoId}`}
        src={`https://www.tiktok.com/player/v1/${videoId}?${params.toString()}`}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; fullscreen; gyroscope; picture-in-picture; web-share"
        allowFullScreen
        referrerPolicy="strict-origin-when-cross-origin"
        onLoad={() => setLoaded(true)}
        className={loaded ? "opacity-100 transition-opacity" : "opacity-0"}
      />
    </div>
  );
});
