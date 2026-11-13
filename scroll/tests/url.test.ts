import { describe, expect, it } from "vitest";
import { parseContentUrl } from "@/lib/content/url";

describe("parseContentUrl", () => {
  it("parses YouTube watch, shorts, youtu.be and embed URLs", () => {
    for (const url of [
      "https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=10s",
      "https://youtube.com/shorts/aqz-KE-bpKQ",
      "https://youtu.be/aqz-KE-bpKQ",
      "https://www.youtube-nocookie.com/embed/aqz-KE-bpKQ",
      "youtube.com/watch?v=aqz-KE-bpKQ",
    ]) {
      expect(parseContentUrl(url)).toEqual({ provider: "youtube", externalId: "aqz-KE-bpKQ", canonicalUrl: "https://www.youtube.com/watch?v=aqz-KE-bpKQ" });
    }
  });

  it("parses TikTok video URLs", () => {
    expect(parseContentUrl("https://www.tiktok.com/@scout2015/video/6718335390845095173?lang=en")).toEqual({
      provider: "tiktok",
      externalId: "6718335390845095173",
      canonicalUrl: "https://www.tiktok.com/@scout2015/video/6718335390845095173",
    });
  });

  it("parses Instagram posts and reels", () => {
    expect(parseContentUrl("https://www.instagram.com/reel/C3Q1Z0ZxK9L/?igsh=abc")?.canonicalUrl).toBe("https://www.instagram.com/reel/C3Q1Z0ZxK9L/");
    expect(parseContentUrl("https://instagram.com/p/C3Q1Z0ZxK9L")?.externalId).toBe("C3Q1Z0ZxK9L");
    expect(parseContentUrl("https://www.instagram.com/nasa/reel/C3Q1Z0ZxK9L/")?.provider).toBe("instagram");
  });

  it("parses X and Twitter status URLs", () => {
    expect(parseContentUrl("https://twitter.com/jack/status/20")).toEqual({ provider: "x", externalId: "20", canonicalUrl: "https://x.com/jack/status/20" });
    expect(parseContentUrl("https://x.com/jack/status/20?s=20")?.provider).toBe("x");
  });

  it("parses Reddit permalinks and redd.it short links", () => {
    expect(parseContentUrl("https://www.reddit.com/r/videos/comments/abc123/some_title/")).toEqual({
      provider: "reddit",
      externalId: "abc123",
      canonicalUrl: "https://www.reddit.com/r/videos/comments/abc123/some_title/",
    });
    expect(parseContentUrl("https://redd.it/abc123")?.externalId).toBe("abc123");
  });

  it("rejects unsupported or malformed input", () => {
    expect(parseContentUrl("https://example.com/video/1")).toBeNull();
    expect(parseContentUrl("not a url")).toBeNull();
    expect(parseContentUrl("https://www.youtube.com/watch?v=short")).toBeNull();
    expect(parseContentUrl("ftp://youtube.com/watch?v=aqz-KE-bpKQ")).toBeNull();
  });
});
