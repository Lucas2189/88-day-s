import type { ProviderId } from "@/lib/content/types";

/**
 * Simplified monochrome platform glyphs for identification purposes only
 * (nominative use). Replace with official brand assets per each platform's
 * brand guidelines before a public launch.
 */
export function ProviderLogo({ provider, size = 16, className }: { provider: ProviderId; size?: number; className?: string }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "currentColor", className, "aria-hidden": true } as const;
  switch (provider) {
    case "youtube":
      return (
        <svg {...common}>
          <path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1c.4-1.6.5-3.2.5-4.8s-.1-3.2-.5-4.8ZM9.8 15.1V8.9L15.6 12l-5.8 3.1Z" />
        </svg>
      );
    case "tiktok":
      return (
        <svg {...common}>
          <path d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.2v13a2.7 2.7 0 1 1-2.7-2.7c.3 0 .6 0 .8.1V10a6 6 0 1 0 5.1 5.9V9.4a7.4 7.4 0 0 0 4.4 1.4V7.6a4.4 4.4 0 0 1-3.3-1.8Z" />
        </svg>
      );
    case "instagram":
      return (
        <svg {...common}>
          <path d="M12 7.3a4.7 4.7 0 1 0 0 9.4 4.7 4.7 0 0 0 0-9.4Zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6Zm5.9-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0ZM21 7.1a5.5 5.5 0 0 0-1.5-3.9A5.5 5.5 0 0 0 15.6 1.7C14.1 1.6 9.9 1.6 8.4 1.7a5.5 5.5 0 0 0-3.9 1.5A5.5 5.5 0 0 0 3 7.1c-.1 1.5-.1 5.7 0 7.2a5.5 5.5 0 0 0 1.5 3.9 5.5 5.5 0 0 0 3.9 1.5c1.5.1 5.7.1 7.2 0a5.5 5.5 0 0 0 3.9-1.5 5.5 5.5 0 0 0 1.5-3.9c.1-1.5.1-5.7 0-7.2Zm-2 8.8a3 3 0 0 1-1.7 1.7c-1.2.5-4 .4-5.3.4s-4.1.1-5.3-.4a3 3 0 0 1-1.7-1.7c-.5-1.2-.4-4-.4-5.3s-.1-4.1.4-5.3A3 3 0 0 1 6.7 3.6c1.2-.5 4-.4 5.3-.4s4.1-.1 5.3.4a3 3 0 0 1 1.7 1.7c.5 1.2.4 4 .4 5.3s.1 4.1-.4 5.3Z" />
        </svg>
      );
    case "x":
      return (
        <svg {...common}>
          <path d="M18.2 2.3h3.4l-7.4 8.4L23 21.7h-6.8l-5.3-6.9-6.1 6.9H1.4l7.9-9L1 2.3h7l4.8 6.3 5.4-6.3Zm-1.2 17.4h1.9L7.1 4.2H5.1l11.9 15.5Z" />
        </svg>
      );
    case "reddit":
      return (
        <svg {...common}>
          <path d="M22 12.1a2.2 2.2 0 0 0-3.7-1.6 10.8 10.8 0 0 0-5.8-1.8l1-4.7 3.2.7a1.6 1.6 0 1 0 .2-.8l-3.6-.8a.4.4 0 0 0-.5.3l-1.1 5.3a10.8 10.8 0 0 0-5.9 1.8 2.2 2.2 0 1 0-2.4 3.6 4.3 4.3 0 0 0 0 .7c0 3.4 3.9 6.1 8.7 6.1s8.7-2.7 8.7-6.1a4.3 4.3 0 0 0 0-.7 2.2 2.2 0 0 0 1.2-2ZM7 13.6a1.6 1.6 0 1 1 3.2 0 1.6 1.6 0 0 1-3.2 0Zm8.9 4.2a5.8 5.8 0 0 1-3.9 1.2 5.8 5.8 0 0 1-3.9-1.2.4.4 0 0 1 .6-.6 5 5 0 0 0 3.3 1 5 5 0 0 0 3.3-1 .4.4 0 0 1 .6.6Zm-.3-2.6a1.6 1.6 0 1 1 0-3.2 1.6 1.6 0 0 1 0 3.2Z" />
        </svg>
      );
  }
}
