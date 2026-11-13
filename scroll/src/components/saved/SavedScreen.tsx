"use client";

import { FolderPlus, Play, Search, Trash2 } from "lucide-react";
import Link from "next/link";
import { useMemo, useState } from "react";
import { Chip } from "@/components/ui/Chip";
import { ProviderBadge, PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { SmartImage } from "@/components/ui/SmartImage";
import { useToast } from "@/components/ui/Toast";
import { PROVIDER_IDS, type ProviderId } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

export function SavedScreen() {
  const bookmarks = useUserStore((s) => s.bookmarks);
  const collections = useUserStore((s) => s.collections);
  const createCollection = useUserStore((s) => s.createCollection);
  const deleteCollection = useUserStore((s) => s.deleteCollection);
  const toggleBookmark = useUserStore((s) => s.toggleBookmark);
  const { toast } = useToast();
  const [query, setQuery] = useState("");
  const [collectionId, setCollectionId] = useState<string | null>(null);
  const [provider, setProvider] = useState<ProviderId | null>(null);

  const list = useMemo(() => {
    const q = query.trim().toLowerCase();
    return Object.values(bookmarks)
      .filter((b) => !collectionId || b.collectionIds.includes(collectionId))
      .filter((b) => !provider || b.item.provider === provider)
      .filter((b) => !q || [b.item.title, b.item.authorName, b.item.description, b.note].join(" ").toLowerCase().includes(q))
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }, [bookmarks, collectionId, provider, query]);

  const collectionList = Object.values(collections).sort((a, b) => a.name.localeCompare(b.name));
  const total = Object.keys(bookmarks).length;

  return (
    <div className="min-h-dvh pb-[calc(var(--tabbar-h)+var(--safe-bottom)+24px)]" style={{ paddingTop: "var(--safe-top)" }}>
      <header className="sticky top-0 z-30 bg-black/85 px-4 pb-3 pt-4 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          <h1 className="font-display text-2xl font-semibold">Saved</h1>
          <button
            type="button"
            onClick={() => {
              const name = window.prompt("Collection name");
              if (name?.trim()) {
                createCollection(name);
                toast("Collection created", "success");
              }
            }}
            className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white/[0.08] px-3.5 py-2 text-xs font-semibold"
          >
            <FolderPlus size={14} /> New
          </button>
        </div>
        <label className="mt-3 flex h-11 items-center gap-2 rounded-full border border-line bg-surface-2 px-4">
          <Search size={16} className="text-fg-faint" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search your saves" className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-fg-faint" type="search" aria-label="Search saved" />
        </label>
        <div className="no-scrollbar -mx-4 mt-3 flex gap-2 overflow-x-auto px-4">
          <Chip size="sm" active={collectionId === null} onClick={() => setCollectionId(null)}>
            All ({total})
          </Chip>
          {collectionList.map((c) => (
            <Chip key={c.id} size="sm" active={collectionId === c.id} onClick={() => setCollectionId(c.id)}>
              {c.emoji ?? "📁"} {c.name}
            </Chip>
          ))}
        </div>
        <div className="no-scrollbar -mx-4 mt-2 flex gap-2 overflow-x-auto px-4">
          <Chip size="sm" active={provider === null} onClick={() => setProvider(null)}>
            All platforms
          </Chip>
          {PROVIDER_IDS.map((p) => (
            <Chip key={p} size="sm" active={provider === p} onClick={() => setProvider(p)}>
              {PROVIDER_NAMES[p]}
            </Chip>
          ))}
        </div>
      </header>

      {collectionId && (
        <div className="flex items-center justify-between px-4 pt-2">
          <Link href={`/?scope=saved&collection=${collectionId}`} className="inline-flex items-center gap-1.5 rounded-full bg-white px-3.5 py-2 text-xs font-semibold text-black">
            <Play size={14} fill="currentColor" /> Play collection
          </Link>
          <button
            type="button"
            onClick={() => {
              if (window.confirm("Delete this collection? Saved items are kept.")) {
                deleteCollection(collectionId);
                setCollectionId(null);
              }
            }}
            className="inline-flex items-center gap-1 text-xs text-fg-muted"
          >
            <Trash2 size={14} /> Delete collection
          </button>
        </div>
      )}

      {total === 0 ? (
        <div className="px-8 pt-24 text-center">
          <p className="font-display text-xl font-semibold">Nothing saved yet</p>
          <p className="mt-2 text-sm text-fg-muted">Tap the bookmark on any item to keep it here, across every platform.</p>
          <Link href="/" className="mt-5 inline-flex rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-black">
            Go to feed
          </Link>
        </div>
      ) : (
        <ul className="mt-3 space-y-2 px-4">
          {list.map((b) => (
            <li key={b.contentId} className="flex gap-3 rounded-2xl border border-line bg-surface-2 p-2">
              <Link href={`/?item=${encodeURIComponent(b.contentId)}`} className="relative h-24 w-20 shrink-0 overflow-hidden rounded-xl bg-surface-3">
                {b.item.thumbnailUrl && (
                  <SmartImage src={b.item.thumbnailUrl} cropLetterbox className="h-full w-full object-cover" />
                )}
                <ProviderBadge provider={b.item.provider} compact className="absolute left-1 top-1 px-1.5 py-0.5" />
              </Link>
              <div className="min-w-0 flex-1 py-1">
                <Link href={`/?item=${encodeURIComponent(b.contentId)}`} className="line-clamp-2 text-sm font-semibold leading-tight">
                  {b.item.title}
                </Link>
                <p className="mt-1 line-clamp-1 text-xs text-fg-muted">{b.item.authorName}</p>
                <div className="mt-2 flex items-center gap-3 text-xs">
                  <a href={b.item.url} target="_blank" rel="noopener noreferrer" className="text-fg-muted underline-offset-2 hover:underline">
                    Open original
                  </a>
                  <button type="button" onClick={() => toggleBookmark(b.item)} className="text-fg-faint hover:text-red-300">
                    Remove
                  </button>
                </div>
                {b.collectionIds.length > 0 && (
                  <p className="mt-1 truncate text-[11px] text-fg-faint">{b.collectionIds.map((id) => collections[id]?.name).filter(Boolean).join(" · ")}</p>
                )}
              </div>
            </li>
          ))}
          {list.length === 0 && <p className="pt-10 text-center text-sm text-fg-muted">No saved items match these filters.</p>}
        </ul>
      )}
    </div>
  );
}
