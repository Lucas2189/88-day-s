# SCROLL — One app. One feed. Every social network.

SCROLL is a mobile-first PWA that lets people discover supported content from **YouTube, TikTok,
Instagram, X and Reddit** inside one vertical, TikTok-style feed, with universal bookmarks, source
controls and an on-device personalization engine.

> Honesty rule baked into the product: SCROLL only uses **official** embeds and APIs. No platform exposes its
> personalized recommendation feed to third parties, so SCROLL's "For you" is its **own** ranking over
> content that is legitimately reachable (demo items, links you add, and provider APIs when configured).
> Everything unsupported is shown as unavailable in the app (Discover → Sources, Profile → Sources).
> Full analysis: [`docs/feasibility.md`](docs/feasibility.md). Design: [`docs/architecture.md`](docs/architecture.md).

## Status of integrations (2026-11-13)

| Platform | Paste a public link | In-app playback | Discovery feed | Search | Needs |
|---|---|---|---|---|---|
| YouTube | ✅ oEmbed / Data API | ✅ official IFrame Player (muted autoplay, unmute, progress) | ⚠️ from public playlists you configure | ⚠️ 100 calls/day | `YOUTUBE_API_KEY` for feed/search |
| TikTok | ✅ oEmbed | ✅ official Embed Player (autoplay, mute, events) | ❌ no public API | ❌ | nothing |
| Instagram | ✅ Meta oEmbed (tokenless) | ⚠️ official embed widget (Instagram controls playback) | ❌ no public API | ❌ | optional `META_APP_ID` + `META_CLIENT_TOKEN` |
| X | ✅ oEmbed | ⚠️ official embed widget | ❌ paid API only | ❌ | nothing |
| Reddit | ✅ (with approved app) / ⚠️ link only | ✅ official embed widget | ⚠️ subreddit listings with approved app | ⚠️ with approved app | `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` |

✅ implemented · ⚠️ implemented with conditions · ❌ not possible through authorized means (visibly unavailable in-app).

## Features

* **Universal vertical feed**: fullscreen snap scrolling, one item at a time, platform badge, open
  original, like, save, share (native share sheet), hide content / hide author, "why am I seeing this".
* **Playback**: official players only; muted autoplay with a speaker button; errors (private, embedding
  disabled, removed) fall back to a "watch on the original platform" card.
* **Personalization**: transparent score (interests, learned affinity from in-app signals, recency,
  exploration, seen/skip penalties). Signals: dwell time, skips, completes, likes, saves, hides, shares,
  opens. Nothing is read from external accounts.
* **Universal bookmarks**: saved items, custom collections, search & filters, original links, "play a
  collection" as a feed, cloud sync when signed in.
* **Controls**: enable/disable sources, mixed vs per-platform feed, interests, exploration slider, autoplay
  and mute preferences.
* **Search**: catalog + provider APIs that allow search; the UI states which sources were searched.
* **Add a link**: paste any public URL from the five platforms; it is resolved server-side and joins the feed.
* **PWA**: manifest, icons, service worker (app shell + offline page), iOS standalone support.
* **Production basics**: loading skeletons, error boundaries, typed API errors, per-IP rate limiting,
  server-side TTL cache, no secrets on the client, keyboard navigation, ARIA labels, reduced-motion support.

## Quick start

```bash
cd scroll
npm install
cp .env.example .env.local        # optional: everything runs without keys (local mode)
npm run dev                        # http://localhost:3000
```

Open it on your phone (same Wi-Fi) or in Chrome DevTools device mode; on iOS Safari use **Share → Add to
Home Screen** to install the PWA (service worker is active in production builds: `npm run build && npm start`).

### Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Dev server (Turbopack) |
| `npm run build` / `npm start` | Production build / server |
| `npm run lint` | ESLint (Next core-web-vitals + TypeScript) |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Vitest unit tests (URL parser, ranking, adapters, store) |
| `npm run e2e` | Playwright smoke test on an emulated iPhone against `BASE_URL` (default `http://localhost:3100`): tabs, like/save/hide, filters, add-link success & failure, search, manifest. Screenshots in `e2e-shots/` |
| `npm run seed:demo` | Re-resolves the demo catalog (`src/lib/demo/catalog.json`) from real public URLs through the adapters |

## Configuration

All variables are optional; see [`.env.example`](.env.example) for the full list and where to get each key.

| Variable | Unlocks |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Magic-link sign-in and cloud sync of preferences, bookmarks, collections, hidden lists, engagement events |
| `YOUTUBE_API_KEY` (+ `YOUTUBE_FEED_PLAYLIST_IDS`) | Richer YouTube metadata (duration, category, stats), playlist-based discovery feed, search |
| `META_APP_ID`, `META_CLIENT_TOKEN` | Higher Instagram oEmbed rate limits |
| `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` (+ `REDDIT_FEED_SUBREDDITS`) | Reddit metadata, subreddit feed, search (approved non-commercial app required) |

Server-only keys never reach the browser: all provider calls happen in `/api/*` route handlers.

## Database (Supabase)

1. Create a Supabase project, enable **Email** auth (magic link) and add `http://localhost:3000/auth/callback`
   (and your production URL) to the redirect allow-list.
2. Run [`supabase/migrations/0001_init.sql`](supabase/migrations/0001_init.sql) in the SQL editor, or with the CLI:
   `supabase db push` (after `supabase link`).
3. Set the two `NEXT_PUBLIC_SUPABASE_*` variables and restart.

Schema: `content_sources`, `content_items` (shared metadata cache), `profiles`, `user_preferences`,
`connected_providers` (for future authorized account links; tokens via Vault), `collections`, `bookmarks`,
`hidden_content`, `engagement_events`, `recommendations`. Every per-user table has RLS (`auth.uid() = user_id`).

## Testing locally

```bash
npm run lint && npm run typecheck && npm test      # static checks + unit tests
npm run build && npx next start -p 3100            # production server in one terminal
npm run e2e                                        # Playwright mobile smoke test in another
```

Manual checklist: swipe the feed (or ↑/↓ keys), tap the speaker to unmute, like/save/hide, switch
"For you" ↔ platform chips, Discover → Add link with a private or wrong URL (clear error) and a valid
one (pinned at the top of the feed), save into a collection and "Play collection", Profile → affinity bars
change after a few interactions, disable a source and check it disappears everywhere.

## Deployment

**Vercel (recommended)**: import the repo, set *Root Directory* to `scroll`, add the environment variables,
deploy. Route handlers run on the Node runtime; the in-memory cache/rate limiter are per instance (swap for
Upstash Redis when scaling, see `docs/architecture.md`).

**Self-hosted / Docker**: `npm run build && npm start` behind any reverse proxy with HTTPS (required for the
service worker and the iOS install prompt). Set `NODE_ENV=production`.

Checklist before going public: official brand assets for the platform glyphs, YouTube API compliance
review if quota > 10k, Reddit data agreement for any monetized build, privacy policy (local + Supabase
storage, no external account access), Content-Security-Policy allowing the five embed origins.

## Project structure

See [`docs/architecture.md`](docs/architecture.md). Short version: `src/lib/providers/*` (one adapter per
platform behind a common interface), `src/lib/ranking/score.ts` (transparent formula), `src/components/feed/*`
(snap feed + embeds), `src/app/api/*` (server routes with cache & rate limiting), `supabase/` (schema + RLS).

## Roadmap after the MVP

Expo / React Native app reusing `src/lib` (see migration guide in the architecture doc), Redis-backed cache,
shared `content_items` cache in Supabase, creator discovery tools, cross-platform collections sharing,
subscription tier (compliant with each platform's terms), clearly labeled sponsorships.
