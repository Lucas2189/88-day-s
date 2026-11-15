export interface PlayerHandle {
  play: () => void;
  pause: () => void;
  mute: () => void;
  unmute: () => void;
}

export type PlayerErrorCode = "invalid" | "cannotPlay" | "notFound" | "embedDisabled" | "generic";

export interface PlayerEvents {
  onReady?: () => void;
  onPlay?: () => void;
  onEnded?: () => void;
  onError?: (code: PlayerErrorCode) => void;
  /** Called when the embedded player reports its own mute state changes. */
  onMuteChange?: (muted: boolean) => void;
}
