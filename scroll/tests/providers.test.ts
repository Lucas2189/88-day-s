import { afterEach, describe, expect, it, vi } from "vitest";
import { resolveUrl, listProviderInfo } from "@/lib/providers/registry";
import { ProviderError } from "@/lib/providers/types";
import { splitScript } from "@/lib/providers/oembed";

function mockFetch(status: number, body: unknown) {
  const fn = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } }));
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("provider registry", () => {
  it("exposes five providers with honest capabilities in local mode", () => {
    const infos = listProviderInfo();
    expect(infos.map((i) => i.id)).toEqual(["youtube", "tiktok", "instagram", "x", "reddit"]);
    for (const info of infos) expect(info.capabilities.resolveUrl).toBe(true);
    expect(infos.find((i) => i.id === "tiktok")?.capabilities.feed).toBe(false);
    expect(infos.find((i) => i.id === "x")?.capabilities.search).toBe(false);
  });

  it("resolves a YouTube URL through oEmbed into the unified model", async () => {
    const fetch = mockFetch(200, { title: "Big Buck Bunny", author_name: "Blender", author_url: "https://www.youtube.com/@BlenderOfficial", thumbnail_url: "https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg", html: "<iframe></iframe>" });
    const item = await resolveUrl("https://youtu.be/aqz-KE-bpKQ", { categories: ["film"] });
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(String(fetch.mock.calls[0][0])).toContain("https://www.youtube.com/oembed?url=");
    expect(item).toMatchObject({ id: "youtube:aqz-KE-bpKQ", provider: "youtube", title: "Big Buck Bunny", categories: ["film"], embed: { type: "youtube-player", videoId: "aqz-KE-bpKQ" } });
  });

  it("maps a 404 from the provider to a ProviderError(not_found)", async () => {
    mockFetch(404, { error: "nope" });
    await expect(resolveUrl("https://www.tiktok.com/@u/video/123456789")).rejects.toMatchObject({ code: "not_found", provider: "tiktok" } satisfies Partial<ProviderError>);
  });

  it("rejects unsupported URLs without any network call", async () => {
    const fetch = mockFetch(200, {});
    await expect(resolveUrl("https://example.com/foo")).rejects.toBeInstanceOf(ProviderError);
    expect(fetch).not.toHaveBeenCalled();
  });

  it("strips the loader script from X oEmbed HTML and keeps the blockquote", async () => {
    mockFetch(200, { url: "https://x.com/jack/status/20", author_name: "jack", author_url: "https://x.com/jack", html: '<blockquote class="twitter-tweet"><p>just setting up my twttr</p></blockquote>\n<script async src="https://platform.twitter.com/widgets.js"></script>' });
    const item = await resolveUrl("https://x.com/jack/status/20");
    expect(item.embed).toMatchObject({ type: "oembed-html", scriptSrc: "https://platform.twitter.com/widgets.js" });
    expect((item.embed as { html: string }).html).not.toContain("<script");
    expect(item.title).toContain("just setting up my twttr");
    expect(item.authorName).toBe("@jack");
  });

  it("builds a Reddit link embed without credentials and labels missing metadata", async () => {
    const fetch = mockFetch(200, {});
    const item = await resolveUrl("https://www.reddit.com/r/videos/comments/abc123/title/");
    expect(fetch).not.toHaveBeenCalled();
    expect(item.embed).toMatchObject({ type: "oembed-html", scriptSrc: "https://embed.reddit.com/widgets.js" });
    expect(item.description).toMatch(/credentials/i);
  });
});

describe("splitScript", () => {
  it("extracts protocol-relative script sources", () => {
    const { html, scriptSrc } = splitScript('<blockquote></blockquote><script async src="//www.instagram.com/embed.js"></script>');
    expect(scriptSrc).toBe("https://www.instagram.com/embed.js");
    expect(html).toBe("<blockquote></blockquote>");
  });
});
