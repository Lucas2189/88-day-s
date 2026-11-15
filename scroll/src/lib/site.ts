/** Deployment-level settings shown on public pages. Configure through environment variables. */
export const SITE = {
  name: "SCROLL",
  tagline: "One app. One feed. Every social network.",
  description: "Discover supported content from YouTube, TikTok, Instagram, X and Reddit in one vertical feed, and keep your saves from every platform in one place.",
  /** Public base URL (used for canonical links, sitemap and social previews). */
  url:
    process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") ??
    (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : "http://localhost:3000"),
  /** Legal entity or person operating this deployment. */
  operator: process.env.NEXT_PUBLIC_OPERATOR_NAME?.trim() || "the operator of this SCROLL deployment",
  /** Contact address for privacy, legal and rights-holder requests. */
  contactEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL?.trim() || "",
  legalUpdated: "15 November 2026",
} as const;
