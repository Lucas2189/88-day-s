import type { ProviderId } from "./types";

export interface ParsedContentUrl {
  provider: ProviderId;
  externalId: string;
  canonicalUrl: string;
}

const YT_ID = /^[A-Za-z0-9_-]{11}$/;

function clean(input: string): URL | null {
  try {
    const trimmed = input.trim();
    const withScheme = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
    const url = new URL(withScheme);
    if (url.protocol !== "https:" && url.protocol !== "http:") return null;
    return url;
  } catch {
    return null;
  }
}

/**
 * Parses a public URL into a provider + external id. Pure function, no network.
 * Returns null for unsupported hosts so the caller can present a clear error.
 */
export function parseContentUrl(input: string): ParsedContentUrl | null {
  const url = clean(input);
  if (!url) return null;
  const host = url.hostname.replace(/^www\.|^m\.|^mobile\./, "").toLowerCase();
  const parts = url.pathname.split("/").filter(Boolean);

  // YouTube: watch?v=, /shorts/, /embed/, /live/, youtu.be/
  if (host === "youtube.com" || host === "youtube-nocookie.com" || host === "youtu.be") {
    let id: string | undefined;
    if (host === "youtu.be") id = parts[0];
    else if (parts[0] === "shorts" || parts[0] === "embed" || parts[0] === "live" || parts[0] === "v") id = parts[1];
    else if (parts[0] === "watch") id = url.searchParams.get("v") ?? undefined;
    if (id && YT_ID.test(id)) {
      return { provider: "youtube", externalId: id, canonicalUrl: `https://www.youtube.com/watch?v=${id}` };
    }
    return null;
  }

  // TikTok: /@user/video/123, /t/short, vm.tiktok.com/short (short links need network; unsupported offline)
  if (host === "tiktok.com") {
    const videoIdx = parts.indexOf("video");
    if (videoIdx >= 0 && parts[videoIdx + 1] && /^\d{5,}$/.test(parts[videoIdx + 1])) {
      const user = parts[0]?.startsWith("@") ? parts[0] : "@tiktok";
      const id = parts[videoIdx + 1];
      return { provider: "tiktok", externalId: id, canonicalUrl: `https://www.tiktok.com/${user}/video/${id}` };
    }
    if (parts[0] === "embed" && parts[1] && /^\d{5,}$/.test(parts[1])) {
      return { provider: "tiktok", externalId: parts[1], canonicalUrl: `https://www.tiktok.com/@tiktok/video/${parts[1]}` };
    }
    return null;
  }

  // Instagram: /p/{code}, /reel/{code}, /reels/{code}, /tv/{code}
  if (host === "instagram.com") {
    const kinds = new Set(["p", "reel", "reels", "tv"]);
    let i = 0;
    // Allow /{username}/reel/{code}
    if (parts.length >= 3 && !kinds.has(parts[0]) && kinds.has(parts[1])) i = 1;
    if (kinds.has(parts[i]) && parts[i + 1] && /^[A-Za-z0-9_-]{5,}$/.test(parts[i + 1])) {
      const code = parts[i + 1];
      const kind = parts[i] === "reels" ? "reel" : parts[i];
      return { provider: "instagram", externalId: code, canonicalUrl: `https://www.instagram.com/${kind}/${code}/` };
    }
    return null;
  }

  // X / Twitter: /{user}/status/{id}
  if (host === "x.com" || host === "twitter.com" || host === "fxtwitter.com") {
    const statusIdx = parts.indexOf("status");
    if (statusIdx === 1 && parts[2] && /^\d+$/.test(parts[2])) {
      const id = parts[2];
      return { provider: "x", externalId: id, canonicalUrl: `https://x.com/${parts[0]}/status/${id}` };
    }
    return null;
  }

  // Reddit: /r/{sub}/comments/{id}/{slug}, redd.it/{id}
  if (host === "reddit.com" || host === "old.reddit.com" || host === "new.reddit.com" || host === "redd.it") {
    if (host === "redd.it" && parts[0] && /^[a-z0-9]{4,10}$/i.test(parts[0])) {
      return { provider: "reddit", externalId: parts[0], canonicalUrl: `https://www.reddit.com/comments/${parts[0]}/` };
    }
    const cIdx = parts.indexOf("comments");
    if (cIdx >= 0 && parts[cIdx + 1] && /^[a-z0-9]{4,10}$/i.test(parts[cIdx + 1])) {
      const id = parts[cIdx + 1];
      const sub = parts[0] === "r" && parts[1] ? `r/${parts[1]}/` : "";
      const slug = parts[cIdx + 2] ? `${parts[cIdx + 2]}/` : "";
      return { provider: "reddit", externalId: id, canonicalUrl: `https://www.reddit.com/${sub}comments/${id}/${slug}` };
    }
    return null;
  }

  return null;
}

export function contentId(provider: ProviderId, externalId: string): string {
  return `${provider}:${externalId}`;
}
