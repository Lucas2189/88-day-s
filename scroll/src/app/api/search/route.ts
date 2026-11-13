import { NextResponse } from "next/server";
import type { ContentItem, ProviderId } from "@/lib/content/types";
import { DEMO_ITEMS } from "@/lib/demo/catalog";
import { getAdapter, listProviderInfo } from "@/lib/providers/registry";
import { enforceRateLimit } from "@/lib/server/http";

export interface SearchResponse {
  query: string;
  items: ContentItem[];
  /** Per-provider outcome so the UI can state which sources were actually searched. */
  sources: { provider: ProviderId; searched: boolean; count: number; reason?: string }[];
}

function matchesCatalog(item: ContentItem, q: string): boolean {
  const hay = [item.title, item.description, item.authorName, ...(item.tags ?? []), ...item.categories].join(" ").toLowerCase();
  return q.split(/\s+/).every((term) => hay.includes(term));
}

/** GET /api/search?q=term → SearchResponse (catalog + provider APIs that support search) */
export async function GET(request: Request) {
  const limited = enforceRateLimit(request, "search", 15, 0.25);
  if (limited) return limited;
  const q = (new URL(request.url).searchParams.get("q") ?? "").trim().toLowerCase().slice(0, 100);
  if (q.length < 2) return NextResponse.json({ query: q, items: [], sources: [] } satisfies SearchResponse);

  const items: ContentItem[] = DEMO_ITEMS.filter((it) => matchesCatalog(it, q));
  const sources: SearchResponse["sources"] = [];

  await Promise.all(
    listProviderInfo().map(async (info) => {
      const adapter = getAdapter(info.id);
      if (!info.capabilities.search || !adapter.search) {
        sources.push({ provider: info.id, searched: false, count: 0, reason: "No public search API available or credentials missing." });
        return;
      }
      try {
        const found = await adapter.search({ query: q, limit: 12 });
        items.push(...found);
        sources.push({ provider: info.id, searched: true, count: found.length });
      } catch (err) {
        sources.push({ provider: info.id, searched: false, count: 0, reason: (err as Error).message });
      }
    }),
  );

  const seen = new Set<string>();
  const deduped = items.filter((it) => (seen.has(it.id) ? false : (seen.add(it.id), true)));
  return NextResponse.json({ query: q, items: deduped, sources } satisfies SearchResponse, {
    headers: { "cache-control": "public, max-age=120" },
  });
}
