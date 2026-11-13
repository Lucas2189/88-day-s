import type { CategoryId, ContentItem, FeedResponse, ProviderId } from "@/lib/content/types";
import { DEMO_ITEMS } from "@/lib/demo/catalog";
import { getAdapter, listProviderInfo } from "@/lib/providers/registry";
import { namedCache } from "./cache";

export interface BuildFeedOptions {
  providers?: ProviderId[];
  categories?: CategoryId[];
  includeDemo?: boolean;
  limit?: number;
}

/**
 * Assembles the candidate pool for the feed. Provider APIs are called only when configured; demo items
 * fill the rest so the app is always usable. Ranking happens client-side with the user's private signals.
 */
export async function buildFeed(opts: BuildFeedOptions = {}): Promise<FeedResponse> {
  const providers = listProviderInfo();
  const wanted = opts.providers?.length ? opts.providers : providers.map((p) => p.id);
  const notes: string[] = [];
  const items: ContentItem[] = [];
  const cache = namedCache<ContentItem[]>("feed-provider");

  await Promise.all(
    wanted.map(async (id) => {
      const adapter = getAdapter(id);
      if (!adapter.info.capabilities.feed || !adapter.feed) return;
      const key = `${id}:${(opts.categories ?? []).join(",")}`;
      try {
        let list = cache.get(key);
        if (!list) {
          list = await adapter.feed({ limit: 50, categories: opts.categories });
          cache.set(key, list, 10 * 60 * 1000);
        }
        items.push(...list);
        notes.push(`${adapter.info.name}: ${list.length} items from the official API.`);
      } catch (err) {
        notes.push(`${adapter.info.name}: API feed unavailable (${(err as Error).message}). Falling back to demo/user content.`);
      }
    }),
  );

  if (opts.includeDemo !== false) {
    const demo = DEMO_ITEMS.filter((it) => wanted.includes(it.provider)).filter(
      (it) => !opts.categories?.length || it.categories.some((c) => opts.categories!.includes(c)),
    );
    items.push(...demo);
    if (demo.length) notes.push(`${demo.length} demo items (real public publications resolved through official oEmbed endpoints).`);
  }

  const seen = new Set<string>();
  const deduped = items.filter((it) => (seen.has(it.id) ? false : (seen.add(it.id), true)));

  return {
    items: deduped.slice(0, opts.limit ?? 200),
    providers,
    generatedAt: new Date().toISOString(),
    notes,
  };
}
