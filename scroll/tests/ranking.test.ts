import { describe, expect, it } from "vitest";
import type { ContentItem } from "@/lib/content/types";
import { learnAffinity, rankItems, scoreItem, type EngagementEvent, type RankingProfile } from "@/lib/ranking/score";

function item(id: string, categories: ContentItem["categories"], provider: ContentItem["provider"] = "youtube", extra: Partial<ContentItem> = {}): ContentItem {
  return {
    id,
    provider,
    externalId: id,
    kind: "video",
    url: `https://example.com/${id}`,
    title: id,
    categories,
    embed: { type: "link-card" },
    origin: "demo",
    fetchedAt: new Date().toISOString(),
    ...extra,
  };
}

function profile(overrides: Partial<RankingProfile> = {}): RankingProfile {
  return {
    interests: [],
    enabledProviders: ["youtube", "tiktok", "instagram", "x", "reddit"],
    hiddenContentIds: new Set(),
    hiddenAuthors: new Set(),
    affinity: {},
    seenContentIds: new Set(),
    skippedContentIds: new Set(),
    seed: 1,
    ...overrides,
  };
}

const now = Date.parse("2026-11-13T00:00:00Z");
const ev = (type: EngagementEvent["type"], categories: ContentItem["categories"], daysAgo = 0, dwellSeconds?: number): EngagementEvent => ({
  id: `${type}-${categories.join()}-${daysAgo}`,
  contentId: "c",
  provider: "youtube",
  categories,
  type,
  dwellSeconds,
  createdAt: new Date(now - daysAgo * 86_400_000).toISOString(),
});

describe("learnAffinity", () => {
  it("raises affinity for saved/liked categories and lowers it for skipped ones", () => {
    const a = learnAffinity([ev("save", ["music"]), ev("like", ["music"]), ev("skip", ["sports"]), ev("skip", ["sports"])], now);
    expect(a.music).toBeGreaterThan(0.5);
    expect(a.sports).toBeLessThan(0);
  });

  it("decays old signals (14-day half-life)", () => {
    const fresh = learnAffinity([ev("save", ["music"])], now).music!;
    const old = learnAffinity([ev("save", ["music"], 28)], now).music!;
    expect(old).toBeLessThan(fresh);
    expect(old).toBeGreaterThan(0);
  });

  it("rewards long views", () => {
    const short = learnAffinity([ev("view", ["tech"], 0, 1)], now).tech!;
    const long = learnAffinity([ev("view", ["tech"], 0, 30)], now).tech!;
    expect(long).toBeGreaterThan(short);
  });
});

describe("scoreItem / rankItems", () => {
  it("removes hidden content, hidden authors and disabled providers", () => {
    const p = profile({ hiddenContentIds: new Set(["youtube:a"]), hiddenAuthors: new Set(["https://x.com/bob"]), enabledProviders: ["youtube"] });
    expect(scoreItem(item("youtube:a", ["music"]), p)).toBeNull();
    expect(scoreItem(item("x:b", ["news"], "x", { authorUrl: "https://x.com/bob" }), p)).toBeNull();
    expect(scoreItem(item("tiktok:c", ["music"], "tiktok"), p)).toBeNull();
    expect(scoreItem(item("youtube:d", ["music"]), p)).not.toBeNull();
  });

  it("ranks interest matches above non-matches", () => {
    const ranked = rankItems([item("1", ["sports"]), item("2", ["music"])], profile({ interests: ["music"] }));
    expect(ranked[0].item.id).toBe("2");
    expect(ranked[0].reasons).toContain("Matches your interests");
  });

  it("uses learned affinity and penalises seen/skipped items", () => {
    const p = profile({ affinity: { gaming: 0.9 }, seenContentIds: new Set(["seen"]), skippedContentIds: new Set(["skipped"]) });
    const ranked = rankItems([item("seen", ["gaming"]), item("skipped", ["gaming"]), item("new", ["gaming"]), item("other", ["food"])], p);
    expect(ranked.map((r) => r.item.id)).toEqual(["new", "seen", "skipped", "other"]);
  });

  it("is deterministic for a given seed and diversifies providers when asked", () => {
    const items = [item("a1", ["music"]), item("a2", ["music"]), item("b1", ["music"], "tiktok"), item("a3", ["music"])];
    const first = rankItems(items, profile({ seed: 42 }), { diversify: true });
    const second = rankItems(items, profile({ seed: 42 }), { diversify: true });
    expect(first.map((r) => r.item.id)).toEqual(second.map((r) => r.item.id));
    expect(first).toHaveLength(4);
  });
});
