"use client";

import { Check, FolderPlus, Plus } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Sheet } from "@/components/ui/Sheet";
import type { ContentItem } from "@/lib/content/types";
import { useUserStore } from "@/lib/store/user-store";

export function SaveSheet({ item, open, onClose }: { item: ContentItem | null; open: boolean; onClose: () => void }) {
  const collections = useUserStore((s) => s.collections);
  const bookmark = useUserStore((s) => (item ? s.bookmarks[item.id] : undefined));
  const toggleBookmark = useUserStore((s) => s.toggleBookmark);
  const setBookmarkCollections = useUserStore((s) => s.setBookmarkCollections);
  const createCollection = useUserStore((s) => s.createCollection);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  if (!item) return null;
  const list = Object.values(collections).sort((a, b) => a.name.localeCompare(b.name));
  const selected = new Set(bookmark?.collectionIds ?? []);

  const toggle = (collectionId: string) => {
    if (!bookmark) {
      toggleBookmark(item, collectionId);
      return;
    }
    const next = selected.has(collectionId) ? [...selected].filter((c) => c !== collectionId) : [...selected, collectionId];
    setBookmarkCollections(item.id, next);
  };

  return (
    <Sheet open={open} onClose={onClose} title="Save to collection">
      <div className="space-y-2">
        <button
          type="button"
          onClick={() => {
            toggleBookmark(item);
            if (bookmark) onClose();
          }}
          className="flex w-full items-center justify-between rounded-2xl border border-line bg-surface-2 px-4 py-3 text-left"
        >
          <span>
            <span className="block text-sm font-semibold">{bookmark ? "Saved" : "Save"}</span>
            <span className="block text-xs text-fg-muted">{bookmark ? "Tap to remove from Saved" : "Add to your universal bookmarks"}</span>
          </span>
          {bookmark && <Check size={18} className="text-save" />}
        </button>

        {list.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => toggle(c.id)}
            className="flex w-full items-center justify-between rounded-2xl border border-line bg-surface-2 px-4 py-3 text-left"
          >
            <span className="flex items-center gap-3">
              <span className="text-lg">{c.emoji ?? "📁"}</span>
              <span className="text-sm font-medium">{c.name}</span>
            </span>
            {selected.has(c.id) && <Check size={18} className="text-save" />}
          </button>
        ))}

        {creating ? (
          <form
            className="flex gap-2 pt-1"
            onSubmit={(e) => {
              e.preventDefault();
              if (!newName.trim()) return;
              const c = createCollection(newName);
              toggle(c.id);
              setNewName("");
              setCreating(false);
            }}
          >
            <input
              autoFocus
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Collection name"
              maxLength={40}
              className="h-11 flex-1 rounded-full border border-line bg-surface-2 px-4 text-sm outline-none focus:border-white/40"
            />
            <Button type="submit" size="md">
              <Plus size={16} /> Add
            </Button>
          </form>
        ) : (
          <Button variant="secondary" className="w-full" onClick={() => setCreating(true)}>
            <FolderPlus size={16} /> New collection
          </Button>
        )}
      </div>
    </Sheet>
  );
}
