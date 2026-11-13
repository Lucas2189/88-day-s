"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { useUserStore } from "@/lib/store/user-store";
import { Feed } from "./Feed";
import type { FeedScope } from "./useRankedFeed";

/** Home: the ranked universal feed. `?scope=saved&collection=ID` replays bookmarks; `?item=ID` opens a saved item first; `?open=ID` pins a feed item to the top. */
export function HomeFeed() {
  const params = useSearchParams();
  const bookmarks = useUserStore((s) => s.bookmarks);
  const collections = useUserStore((s) => s.collections);
  const scopeParam = params.get("scope");
  const collectionId = params.get("collection") ?? undefined;
  const itemId = params.get("item");
  const openId = params.get("open");

  const scope: FeedScope = useMemo(() => {
    if (scopeParam === "saved") return { kind: "saved", collectionId };
    if (itemId && bookmarks[itemId]) {
      const first = bookmarks[itemId].item;
      const rest = Object.values(bookmarks)
        .filter((b) => b.contentId !== itemId)
        .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
        .map((b) => b.item);
      return { kind: "items", items: [first, ...rest] };
    }
    return { kind: "home" };
  }, [scopeParam, collectionId, itemId, bookmarks]);

  const title = scope.kind === "saved" ? (collectionId ? collections[collectionId]?.name ?? "Collection" : "Saved") : scope.kind === "items" ? "Saved" : undefined;
  return <Feed scope={scope} title={title} pinFirstId={openId} />;
}
