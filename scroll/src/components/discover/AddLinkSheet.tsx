"use client";

import { useMutation } from "@tanstack/react-query";
import { ClipboardPaste } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { Sheet } from "@/components/ui/Sheet";
import { useToast } from "@/components/ui/Toast";
import { api, ApiClientError } from "@/lib/api/client";
import { CATEGORY_IDS, CATEGORY_LABELS, type CategoryId } from "@/lib/content/types";
import { parseContentUrl } from "@/lib/content/url";
import { useUserStore } from "@/lib/store/user-store";

/** Paste any public YouTube / TikTok / Instagram / X / Reddit link: it is resolved through official endpoints and added to your feed. */
export function AddLinkSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [url, setUrl] = useState("");
  const [categories, setCategories] = useState<CategoryId[]>([]);
  const addSubmitted = useUserStore((s) => s.addSubmitted);
  const { toast } = useToast();
  const router = useRouter();
  const parsed = url.trim() ? parseContentUrl(url) : null;

  const mutation = useMutation({
    mutationFn: () => api.resolve(url.trim(), categories),
    onSuccess: ({ item }) => {
      addSubmitted(item);
      toast("Added to your feed", "success");
      setUrl("");
      setCategories([]);
      onClose();
      router.push(`/?open=${encodeURIComponent(item.id)}`);
    },
  });

  const errorMessage = mutation.error instanceof ApiClientError ? mutation.error.body.error : mutation.error ? (mutation.error as Error).message : null;

  return (
    <Sheet open={open} onClose={onClose} title="Add a link">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (parsed) mutation.mutate();
        }}
        className="space-y-4"
      >
        <div className="flex gap-2">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/shorts/… or any public post URL"
            inputMode="url"
            autoCapitalize="off"
            autoCorrect="off"
            spellCheck={false}
            className="h-12 min-w-0 flex-1 rounded-2xl border border-line bg-surface-2 px-4 text-sm outline-none focus:border-white/40"
            aria-label="Public content URL"
          />
          <button
            type="button"
            aria-label="Paste from clipboard"
            onClick={async () => {
              try {
                setUrl(await navigator.clipboard.readText());
              } catch {
                toast("Clipboard access denied", "error");
              }
            }}
            className="rounded-2xl border border-line bg-surface-2 px-3 text-fg-muted"
          >
            <ClipboardPaste size={18} />
          </button>
        </div>
        {url.trim() && !parsed && <p className="text-xs text-red-300">Unsupported link. Supported: YouTube videos/Shorts, TikTok videos, Instagram posts/Reels, X posts, Reddit posts.</p>}
        {parsed && <p className="text-xs text-emerald-200">Detected: {parsed.provider} · {parsed.externalId}</p>}

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-fg-faint">Topics (optional, improves ranking)</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {CATEGORY_IDS.map((c) => (
              <Chip key={c} size="sm" active={categories.includes(c)} onClick={() => setCategories((cs) => (cs.includes(c) ? cs.filter((x) => x !== c) : [...cs, c].slice(-3)))}>
                {CATEGORY_LABELS[c]}
              </Chip>
            ))}
          </div>
        </div>

        {errorMessage && <p className="rounded-2xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-100">{errorMessage}</p>}

        <Button type="submit" className="w-full" disabled={!parsed} loading={mutation.isPending}>
          Add to my feed
        </Button>
        <p className="text-xs text-fg-faint">Only public content that the platform allows to be embedded can be added. SCROLL stores the link and public metadata, never the media.</p>
      </form>
    </Sheet>
  );
}
