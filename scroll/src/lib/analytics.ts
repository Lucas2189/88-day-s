import { track } from "@vercel/analytics";

/**
 * Privacy-friendly product analytics (Vercel Web Analytics: no cookies, no personal identifiers).
 * Only coarse, anonymous events are sent: never URLs of content, search terms or user ids.
 * Does nothing when analytics is not enabled on the deployment.
 */
export type AnalyticsEvent = "like" | "save" | "share" | "hide" | "open_original" | "add_link" | "search" | "onboarding_done" | "install_hint_dismissed" | "locale_changed";

export function trackEvent(name: AnalyticsEvent, props?: Record<string, string | number | boolean>): void {
  try {
    track(name, props);
  } catch {
    /* analytics must never break the app */
  }
}
