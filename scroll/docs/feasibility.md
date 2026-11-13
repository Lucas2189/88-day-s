# SCROLL · Technical feasibility (verified 2026-11-13)

Scope: what each platform **officially** allows a third-party app to do, and what the MVP therefore implements.
Every row was checked against the vendor's documentation or by calling the public endpoint from this
environment on 2026-11-13. Re-verify before launch: these terms change often.

## Summary matrix

| Platform | Public URL → metadata | In-app playback | Discovery feed | Search | Auth / credentials | Cost | Key restrictions | MVP support |
|---|---|---|---|---|---|---|---|---|
| **YouTube** | ✅ oEmbed (no key), ✅ Data API v3 `videos.list` (key) | ✅ IFrame Player API (muted autoplay, user unmute, progress events) | ⚠️ Only from **public playlists/channels you configure** via `playlistItems.list` (1 unit/page). No access to a user's personalized Home/Shorts feed. | ⚠️ `search.list`, default **100 calls/day** (separate allocation; 10,000 units/day for everything else) | API key for Data API; OAuth only needed for user-owned data (not used) | Free within quota; quota extension requires an audit | Must not overlay UI on the player or alter it; must show YouTube branding; no download. Owner can disable embedding (error 101/150) → fallback link | **Live** (URL + player) · **Partial** (feed/search need key) |
| **TikTok** | ✅ oEmbed `https://www.tiktok.com/oembed` (no key, verified 200) | ✅ Embed Player `player/v1/{id}` (official, supports `autoplay`, `muted`, postMessage play/pause/mute, events). TikTok says "Embed Videos" (blockquote) will be deprecated in favour of the Embed Player | ❌ Display API only lists the **authenticated user's own** videos; Research API is restricted to approved academic/non-profit research. No public "For You" or trending API | ❌ none public | None for oEmbed/player; app review for Display API | Free | Removed/private videos stop working in the embed too; no download, no scraping | **Partial** (URL + player only) |
| **Instagram (Reels)** | ✅ Meta oEmbed `graph.facebook.com/v25.0/instagram_oembed` — **tokenless for public content since 2026-06-15** (Meta blog, verified); app token raises limits | ⚠️ Official `embed.js` blockquote widget. Instagram controls autoplay/mute inside its widget; SCROLL cannot drive it | ❌ Graph API exposes only content owned by connected professional accounts; no public discovery | ❌ none public (hashtag search exists only for business accounts' own use with app review) | Optional `META_APP_ID` + `META_CLIENT_TOKEN` | Free | Public content only; private/age-gated media returns 400 ("Media Not Found"); must not cache beyond `cache_age`; brand rules | **Partial** (URL + widget) |
| **X** | ✅ oEmbed `https://publish.x.com/oembed` (no key, verified 200; `publish.twitter.com` 301-redirects) | ⚠️ Official `widgets.js` embedded post; video playback controlled by X's widget | ❌ X API has no free tier for new developers since Feb 2026; pay-per-use (~$0.005/post read) or legacy Basic $200/mo | ❌ (paid API only) | None for oEmbed | Free for embeds; API is paid | Developer policy forbids replicating the X feed/"off-platform" display of large volumes; embeds must stay unmodified | **Partial** (URL + widget) |
| **Reddit** | ⚠️ With an **approved** OAuth app: `api/info`, listings. Without credentials: no metadata (unauthenticated JSON is blocked from server IPs: verified 403) | ✅ Official embed widget `embed.reddit.com/widgets.js` (blockquote) | ⚠️ Subreddit listings (`/r/x/hot`) with credentials, 100 QPM per client | ⚠️ `/search` with credentials | Registered app; **approval required for every new client since 2025-11-11**; commercial use needs a written agreement | Free tier non-commercial; commercial pricing by contract | Cannot store content beyond what the API terms allow; must honour deletions; NSFW filtering is the app's responsibility | **Partial** (widget), **Live** feed/search with approved credentials |

Legend: ✅ supported and implemented · ⚠️ supported with conditions · ❌ not available through authorized means.

## What "not available" means in the product

* SCROLL **never** has access to another platform's personalized recommendation feed. The "For you" feed is
  SCROLL's own ranking over a candidate pool made of: demo items, links users submit, and provider APIs
  where a key is configured (YouTube playlists, Reddit subreddits).
* Search runs over SCROLL's catalog plus the providers whose API allows search **and** is configured. The
  Discover screen shows which sources were actually searched for each query.
* Playback always goes through the platform's **official** player or widget. No video file is ever fetched,
  proxied, downloaded or stored by SCROLL. Autoplay/mute are only controlled where the player API allows it
  (YouTube, TikTok).
* No overlay is drawn on top of third-party players: the action rail sits beside the media box and the
  metadata below it. This keeps the app compatible with the YouTube API Terms ("do not obscure the player").

## Legal / technical blockers to keep in mind before launch

1. **YouTube API Services Terms**: compliance audit above 10,000 units/day; branding guidelines; no
   "scraping" of metadata outside the API; data retention limited to 30 days for most fields (we cache
   metadata ≤ 6 h in memory and store only bookmarked snapshots).
2. **TikTok**: Embed Player terms + Developer ToS. Deprecation of blockquote embeds means we use only the
   Embed Player. Commercial use of the Research API is not possible.
3. **Meta**: tokenless oEmbed is subject to rate limits "that may differ"; add an app token before scale.
   Instagram's brand guidelines require unmodified embeds.
4. **X**: embeds are fine; any feed-level aggregation would require the paid API and must respect the
   Developer Agreement's restrictions on redistributing content.
5. **Reddit**: commercial use (ads, paid tiers) **requires** a Reddit Data API agreement. Keep the Reddit
   feed disabled in a monetized build until that agreement exists.
6. **Trademarks**: platform names/logos are used for identification only. The glyphs in
   `ProviderLogo.tsx` are placeholders and should be replaced by official brand assets following each
   brand guide.
7. **Browser autoplay policies**: iOS Safari and Chrome require muted autoplay + `playsinline`; sound can
   only start on a user gesture (the speaker button).

## Verification log (2026-11-13)

* `GET https://www.tiktok.com/oembed?url=…` → 200, returns `player/v1` iframe with `autoplay=1&muted=1`.
* `GET https://www.youtube.com/oembed?url=…` → 200 for all demo ids; IFrame API loaded in Playwright.
* `GET https://publish.twitter.com/oembed` → 301 → `https://publish.x.com/oembed` → 200 without auth.
* `GET https://graph.facebook.com/v25.0/instagram_oembed?url=<fake reel>` → 400 "Media Not Found" without token
  (endpoint reachable tokenless; a real public Reel URL is required to confirm end-to-end rendering).
* `GET https://www.reddit.com/r/videos/hot.json` from a datacenter IP → 403 (OAuth required);
  `POST /api/v1/access_token` → 401 without credentials (endpoint reachable); `embed.reddit.com/widgets.js` → 200.
* YouTube quota page: `search.list` has its own 100 calls/day allocation; other list calls cost 1 unit, 10,000/day.
* Meta developer blog (2026-06-15): tokenless oEmbed for Instagram/Facebook/Threads public content.

Sources: developers.tiktok.com/doc/embed-videos & /doc/embed-player · developers.google.com/youtube/v3/determine_quota_cost ·
developers.facebook.com/blog/post/2026/06/15/tokenless-access-to-meta-oembed-apis · developer.x.com/en/docs/x-for-websites/oembed-api ·
support.reddithelp.com Reddit Data API Wiki · redditinc.com/policies/data-api-terms.
