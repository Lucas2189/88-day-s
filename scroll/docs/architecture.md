# SCROLL · Architecture

## Stack

| Layer | Choice | Why |
|---|---|---|
| App | **Next.js 16 (App Router, Turbopack, Cache Components)** + TypeScript | One codebase for the PWA shell, API routes (server-side provider calls, secrets never reach the client) and static prerendering |
| UI | Tailwind CSS v4, `motion` (Framer Motion successor), lucide icons | Fast iteration on a dark, iPhone-first design; spring-based sheets and taps |
| Data | TanStack Query (server data) + zustand/persist (private user state) | Query handles caching/retries of `/api/*`; zustand keeps bookmarks/preferences/events on-device and syncs to Supabase when signed in |
| Backend | Supabase (Postgres, Auth magic link, RLS) — **optional** | The app is fully usable in local mode; Supabase adds identity + multi-device sync |
| Playback | Official players: YouTube IFrame API, TikTok Embed Player, X/Instagram/Reddit embed widgets | Only authorized integration methods (see `docs/feasibility.md`) |
| PWA | `app/manifest.ts` + `public/sw.js` (app-shell cache, offline page) | Installable on iOS/Android home screens; API and third-party traffic are never cached |

Why not a native video player? Every platform forbids fetching the media file directly; only their embeds
are licensed. A Next.js PWA is therefore not a compromise: it is the only architecture that can play all
five sources legally today. The migration path to Expo is described below for store distribution.

## Source layout

```
scroll/
├─ src/app/                  routes: / (feed), /discover, /saved, /profile, /offline, /auth/callback, /api/*
├─ src/components/
│  ├─ feed/                  Feed (snap scroller + IntersectionObserver), FeedItem, ActionRail, sheets, ranking hook
│  ├─ embeds/                YouTubePlayer, TikTokPlayer, OEmbedHtml, EmbedRenderer (strategy switch)
│  ├─ discover/ saved/ profile/ nav/ ui/ providers/
├─ src/lib/
│  ├─ content/               ContentItem model, URL parser (pure, tested)
│  ├─ providers/             ProviderAdapter interface + one adapter per platform + registry
│  ├─ server/                TTL cache, token-bucket rate limiter, feed builder, HTTP helpers
│  ├─ ranking/               transparent scoring + affinity learning (pure, tested)
│  ├─ store/                 zustand user store (persisted), types
│  ├─ supabase/              browser/server clients, sync (pull/merge/push)
│  └─ demo/                  catalog.json generated from real public URLs by scripts/seed-demo.ts
├─ supabase/migrations/      SQL schema + RLS
├─ scripts/                  seed-demo, make-icons, e2e-smoke (Playwright, iPhone emulation)
└─ tests/                    vitest unit tests (url, ranking, providers, store)
```

## Provider adapter contract

```ts
interface ProviderAdapter {
  info: ProviderInfo;                      // capabilities + honest status ("live" | "partial" | "unavailable")
  resolve(externalId, canonicalUrl, ctx): Promise<ContentItem>;   // public URL → unified item (oEmbed/API)
  feed?(opts): Promise<ContentItem[]>;     // only when the platform offers an authorized discovery API
  search?(opts): Promise<ContentItem[]>;   // only when the platform offers an authorized search API
}
```

* Adapters are registered in `providers/registry.ts`; adding a platform = one file + one entry.
* `info` is computed from environment variables so the UI always reflects what is really enabled.
* Every network call goes through the server (`/api/*`) with a TTL cache (`namedCache`) and a per-IP
  token bucket, so provider rate limits are protected even with many clients.
* Errors are typed (`ProviderError` with `not_found | provider_error | unsupported | rate_limited`) and
  mapped to HTTP 404/502/422/429 with human messages that the UI displays verbatim.

### Unified content model

`ContentItem` (`src/lib/content/types.ts`) holds only public metadata (title, author, thumbnail URL,
duration, categories, publication date), the canonical URL and an **embed strategy**:
`youtube-player | tiktok-player | oembed-html | iframe | link-card`. The renderer switches on that strategy,
so the feed component does not know anything platform-specific.

## Feed & playback

1. `/api/feed` assembles a candidate pool: provider feeds (if configured) + demo items, deduplicated.
2. `useRankedFeed` merges the pool with locally submitted links, derives the user's `RankingProfile`
   (interests, enabled sources, hidden sets, learned affinity, session seed) and ranks it **client-side**
   so private signals never leave the device unless the user opts into cloud sync.
3. The order is frozen for the session (recomputed on refresh, filter change or new pool) to avoid feed
   reshuffling while scrolling.
4. `Feed` renders one `FeedItem` per slide inside a CSS `scroll-snap` container. An
   `IntersectionObserver` (threshold 0.6) decides the active slide; only the active slide mounts its
   embed (neighbours show a poster), which keeps memory low and avoids several players fighting for audio.
5. Dwell time is measured per slide: `< 2 s` → `skip`, otherwise `view`; the player's `ENDED` event →
   `complete`. Like/save/hide/share/open are explicit events.

## Ranking formula (MVP, transparent)

```
score = 1.0 · interestMatch        // share of the item's categories in the user's chosen interests (0.5 when none chosen)
      + 1.5 · learnedAffinity      // mean affinity of the item's categories, learned in-app (tanh-squashed, 14-day half-life)
      + 0.6 · sourcePreference     // 1 for enabled sources (0 → removed)
      + 0.3 · recencyBoost         // 1 - ageDays/30 when the publication date is known
      + 0.2 · explorationNoise     // deterministic hash(itemId, sessionSeed) ∈ [0,1)
      - 0.8 · seenPenalty          // already shown in this session
      - 1.2 · skipPenalty          // skipped before
hidden content / hidden authors / disabled sources → excluded
optional greedy diversification: -0.15 if same provider as previous pick, -0.1 if same category
```

Affinity learning weights (per category of the item): save +3, like +2, share +2, complete +1.5, open +1,
view +0.4 (+ up to +1 for dwell ≥ 20 s), skip −1, unlike −1.5, unsave −2, hide −3.
Everything is in `src/lib/ranking/score.ts` and unit-tested. No external engagement signal is used.

Upgrade path: move affinity computation to a Supabase scheduled function writing `recommendations`,
add collaborative signals (item co-saves), then an embedding model for cold-start only when volume
justifies the cost.

## Data & privacy

* Local mode: zustand `persist` in `localStorage` (`scroll:user:v1`). Session-only fields (`seenContentIds`,
  `sessionSeed`) are not persisted.
* Cloud mode: `CloudSync` pulls the remote snapshot at login, merges (union for sets, remote wins for
  preferences), then pushes debounced changes and batches engagement events. RLS guarantees row ownership.
* Stored third-party data = metadata snapshots + links only. No media. YouTube metadata retention limits
  apply to `bookmarks.item` snapshots (refresh or purge after 30 days in a production job).

## Scalability notes

* Replace `namedCache`/`rateLimit` (in-memory) with Upstash Redis when running multiple instances.
* Cache resolved items in `content_items` (Supabase) with the service role to share across users and honour
  provider `cache_age`.
* Feed assembly can move to an edge function + ISR; the client ranking stays cheap (O(n log n) on ≤ 500 items).
* New platforms: add an adapter; the UI, store and ranking need no change.

## Migration to Expo / React Native (App Store & Google Play)

1. Keep `src/lib/**` as a shared package (pure TS: content model, URL parser, ranking, adapters, API client).
2. Keep the Next.js app as the **backend** (`/api/*` routes + Supabase) and PWA.
3. Create an Expo app (`npx create-expo-app`) with Expo Router mirroring the four tabs. Reuse zustand +
   TanStack Query; swap `localStorage` for `expo-secure-store`/`AsyncStorage` via `createJSONStorage`.
4. Playback: use `react-native-youtube-iframe` (wraps the official IFrame API in a WebView) and
   `react-native-webview` for TikTok's Embed Player and the X/Instagram/Reddit widgets, with the same
   `EmbedStrategy` switch. Native video is still not allowed by platform terms.
5. Feed: `FlashList` with `pagingEnabled` + `onViewableItemsChanged` replaces the CSS snap +
   IntersectionObserver.
6. Sharing/bookmarks/haptics via Expo modules; auth via `@supabase/supabase-js` with the Expo auth
   session helper. Ship with EAS Build; keep the web PWA as the universal fallback.
