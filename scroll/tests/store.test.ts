import { beforeEach, describe, expect, it } from "vitest";
import type { ContentItem } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

const item: ContentItem = {
  id: "youtube:x",
  provider: "youtube",
  externalId: "x",
  kind: "video",
  url: "https://www.youtube.com/watch?v=x",
  title: "x",
  authorName: "Author",
  authorUrl: "https://www.youtube.com/@author",
  categories: ["music"],
  embed: { type: "youtube-player", videoId: "x" },
  origin: "demo",
  fetchedAt: new Date().toISOString(),
};

beforeEach(() => {
  localStorage.clear();
  useUserStore.getState().clearAll();
});

describe("user store", () => {
  it("toggles likes and records engagement events", () => {
    const s = useUserStore.getState();
    expect(s.toggleLike(item)).toBe(true);
    expect(useUserStore.getState().likes[item.id]).toBeTruthy();
    expect(useUserStore.getState().events.at(-1)?.type).toBe("like");
    expect(useUserStore.getState().toggleLike(item)).toBe(false);
    expect(useUserStore.getState().events.at(-1)?.type).toBe("unlike");
  });

  it("saves bookmarks into collections and cleans up on collection delete", () => {
    const s = useUserStore.getState();
    const c = s.createCollection("Inspiration", "✨");
    s.toggleBookmark(item, c.id);
    expect(useUserStore.getState().bookmarks[item.id].collectionIds).toEqual([c.id]);
    useUserStore.getState().deleteCollection(c.id);
    expect(useUserStore.getState().collections[c.id]).toBeUndefined();
    expect(useUserStore.getState().bookmarks[item.id].collectionIds).toEqual([]);
  });

  it("hides content and authors", () => {
    useUserStore.getState().hideContent(item, true);
    const s = useUserStore.getState();
    expect(s.hiddenContentIds[item.id]).toBeTruthy();
    expect(s.hiddenAuthors["https://www.youtube.com/@author"]).toBeTruthy();
    s.unhideAll();
    expect(Object.keys(useUserStore.getState().hiddenContentIds)).toHaveLength(0);
  });

  it("persists preferences and bookmarks to localStorage", () => {
    useUserStore.getState().setPreferences({ interests: ["gaming"] });
    useUserStore.getState().toggleBookmark(item);
    const raw = JSON.parse(localStorage.getItem("scroll:user:v1") ?? "{}");
    expect(raw.state.preferences.interests).toEqual(["gaming"]);
    expect(Object.keys(raw.state.bookmarks)).toEqual([item.id]);
    expect(raw.state.seenContentIds).toBeUndefined();
  });
});
