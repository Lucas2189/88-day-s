"use client";

import { useQuery } from "@tanstack/react-query";
import { Link2, Search, X } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Chip } from "@/components/ui/Chip";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { ProviderLogo } from "@/components/ui/ProviderLogo";
import { api } from "@/lib/api/client";
import { CATEGORY_IDS, CATEGORY_LABELS, type CategoryId, type ContentItem } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";
import { AddLinkSheet } from "./AddLinkSheet";
import { ContentCard } from "./ContentCard";
import { SourceStatusList } from "./SourceStatusList";

function useDebounced<T>(value: T, delay = 350): T {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return v;
}

export function DiscoverScreen() {
  const params = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [addOpen, setAddOpen] = useState(params.get("add") === "1");
  const [category, setCategory] = useState<CategoryId | null>(null);
  const debounced = useDebounced(query.trim());
  const submitted = useUserStore((s) => s.submitted);
  const preferences = useUserStore((s) => s.preferences);

  const feed = useQuery({ queryKey: ["feed", "discover"], queryFn: () => api.feed(), staleTime: 5 * 60_000 });
  const search = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => api.search(debounced),
    enabled: debounced.length >= 2,
    staleTime: 2 * 60_000,
  });

  const catalog: ContentItem[] = useMemo(() => {
    const seen = new Set<string>();
    return [...Object.values(submitted), ...(feed.data?.items ?? [])].filter((it) => (seen.has(it.id) ? false : (seen.add(it.id), true)));
  }, [feed.data, submitted]);

  const browse = useMemo(
    () => catalog.filter((it) => preferences.enabledProviders.includes(it.provider)).filter((it) => !category || it.categories.includes(category)),
    [catalog, category, preferences.enabledProviders],
  );

  const showingSearch = debounced.length >= 2;

  return (
    <div className="min-h-dvh pb-[calc(var(--tabbar-h)+var(--safe-bottom)+24px)]" style={{ paddingTop: "var(--safe-top)" }}>
      <header className="sticky top-0 z-30 bg-black/85 px-4 pb-3 pt-4 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <h1 className="font-display text-2xl font-semibold">Discover</h1>
          <button type="button" onClick={() => setAddOpen(true)} className="inline-flex items-center gap-1.5 rounded-full bg-white px-3.5 py-2 text-xs font-semibold text-black">
            <Link2 size={14} /> Add link
          </button>
        </div>
        <label className="mt-3 flex h-11 items-center gap-2 rounded-full border border-line bg-surface-2 px-4">
          <Search size={16} className="text-fg-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search videos, posts, creators…"
            className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-fg-faint"
            type="search"
            inputMode="search"
            aria-label="Search"
          />
          {query && (
            <button type="button" onClick={() => setQuery("")} aria-label="Clear search" className="text-fg-faint">
              <X size={16} />
            </button>
          )}
        </label>
      </header>

      {showingSearch ? (
        <section className="px-4">
          <SearchSources sources={search.data?.sources ?? []} loading={search.isLoading} />
          {search.isError && <p className="mt-3 text-sm text-red-300">{(search.error as Error).message}</p>}
          <div className="mt-3 grid grid-cols-2 gap-3">
            {(search.data?.items ?? []).map((it) => (
              <ContentCard key={it.id} item={it} onOpen={() => openInFeed(router, it)} />
            ))}
          </div>
          {search.isSuccess && search.data.items.length === 0 && <p className="mt-6 text-center text-sm text-fg-muted">No results in the searchable sources. Try adding the link directly.</p>}
        </section>
      ) : (
        <>
          <section className="px-4">
            <div className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-1">
              <Chip size="sm" active={category === null} onClick={() => setCategory(null)}>
                All topics
              </Chip>
              {CATEGORY_IDS.map((c) => (
                <Chip key={c} size="sm" active={category === c} onClick={() => setCategory(c)}>
                  {CATEGORY_LABELS[c]}
                </Chip>
              ))}
            </div>
          </section>

          <section className="mt-4 px-4">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Browse</h2>
            {feed.isLoading ? (
              <div className="mt-3 grid grid-cols-2 gap-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="skeleton aspect-[3/4] rounded-2xl" />
                ))}
              </div>
            ) : (
              <div className="mt-3 grid grid-cols-2 gap-3">
                {browse.map((it) => (
                  <ContentCard key={it.id} item={it} onOpen={() => openInFeed(router, it)} />
                ))}
              </div>
            )}
            {feed.isSuccess && browse.length === 0 && <p className="mt-6 text-center text-sm text-fg-muted">Nothing here yet for this topic. Add a link to seed it.</p>}
          </section>

          <section className="mt-8 px-4">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Sources</h2>
            <p className="mt-1 text-sm text-fg-muted">What each platform officially allows. SCROLL never claims more than this.</p>
            <SourceStatusList providers={feed.data?.providers ?? []} />
          </section>
        </>
      )}

      <AddLinkSheet open={addOpen} onClose={() => setAddOpen(false)} />
    </div>
  );
}

function openInFeed(router: ReturnType<typeof useRouter>, item: ContentItem) {
  // Items that are not in the server pool (e.g. API search results) are kept locally so the feed can show them.
  const store = useUserStore.getState();
  if (!store.submitted[item.id] && item.origin !== "demo") store.addSubmitted(item);
  router.push(`/?open=${encodeURIComponent(item.id)}`);
}

function SearchSources({ sources, loading }: { sources: { provider: string; searched: boolean; count: number; reason?: string }[]; loading: boolean }) {
  if (loading) return <p className="mt-3 text-xs text-fg-faint">Searching…</p>;
  if (!sources.length) return null;
  return (
    <div className="mt-3 flex flex-wrap gap-1.5">
      <span className="rounded-full border border-white/10 bg-white/[0.06] px-2.5 py-1 text-[11px] font-medium text-fg-muted">Catalog ✓</span>
      {sources.map((s) => (
        <span
          key={s.provider}
          title={s.reason}
          className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium ${s.searched ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100" : "border-white/10 bg-white/[0.04] text-fg-faint line-through"}`}
        >
          <ProviderLogo provider={s.provider as keyof typeof PROVIDER_NAMES} size={11} />
          {PROVIDER_NAMES[s.provider as keyof typeof PROVIDER_NAMES]}
        </span>
      ))}
    </div>
  );
}
