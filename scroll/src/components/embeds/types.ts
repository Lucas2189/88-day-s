export interface PlayerHandle {
  play: () => void;
  pause: () => void;
  mute: () => void;
  unmute: () => void;
}

export interface PlayerEvents {
  onReady?: () => void;
  onPlay?: () => void;
  onEnded?: () => void;
  onError?: (message: string) => void;
  /** Called when the embedded player reports its own mute state changes. */
  onMuteChange?: (muted: boolean) => void;
}
