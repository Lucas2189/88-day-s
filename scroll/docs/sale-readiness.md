# SCROLL · Sale readiness and Asia notes (2026-11-15)

This document is for the owner and for a prospective buyer. It lists what the asset is, what has been
verified, what has not, and what a transfer involves. Nothing here is a valuation.

## What the asset is

| Item | State |
|---|---|
| Web app (Next.js 16, TypeScript, PWA) | Complete, production build passes, deployed on Vercel |
| Platforms | YouTube, TikTok, Instagram, X, Reddit through official embeds/oEmbed only (see `feasibility.md`) |
| Languages | 10 UI locales: English, French, Japanese, Korean, Traditional Chinese, Simplified Chinese, Indonesian, Thai, Vietnamese, Hindi. Auto-detected, switchable in Profile |
| Regional relevance | Content region (Japan, Korea, India, Southeast Asia, Chinese-speaking, Global) boosts tagged items; 65-item demo catalog incl. 31 Asia-tagged items |
| Personalization | Transparent on-device ranking, documented formula, unit-tested |
| Accounts and sync | Supabase schema with RLS + magic-link sign-in, optional (not enabled on the live deployment) |
| Trust pages | About, Privacy policy, Terms of use (English), platform-required notices (YouTube API Services) |
| Measurement | Cookieless analytics events (Vercel Web Analytics), off until enabled in the Vercel dashboard |
| Quality | 41 unit tests, Playwright smoke test on emulated iPhone in 7 locales, ESLint + TypeScript clean |
| Documentation | README, feasibility matrix, architecture, this file |

## What is NOT there (be upfront with buyers)

* **No users, no revenue, no traction data yet.** Buyers of pre-revenue projects pay for the cost to
  rebuild and for evidence of demand. Evidence is the cheapest thing to add (see "Raising the price").
* **No native iOS/Android app.** The PWA installs from the browser. A store release needs a wrapper or an
  Expo port (see `architecture.md`) and faces App Store guideline 4.2.2 on content aggregators.
* **No access to platform recommendation feeds.** Not obtainable through authorized means.
* **Embedded playback of the Asia demo items was not verified.** Titles and channels were verified through
  YouTube oEmbed; whether each owner allows embedded playback can only be checked from a normal device or
  with a YouTube Data API key (`status.embeddable`, already honoured by the adapter). Items that refuse
  embedding show a "watch on the original platform" card.
* **Translations were machine-written and not reviewed by native speakers.** Budget a review per language
  before marketing in that country.
* **Legal pages are templates.** They state how the product really works, but have not been reviewed by a
  lawyer. Local privacy laws apply per market (for example APPI in Japan, PIPA in South Korea, the DPDP Act
  in India, PDPA regimes in Thailand and Singapore, PDP Law in Indonesia).
* **Platform glyphs are placeholders**, to be replaced by official brand assets per each brand guide.
* **Demo catalog has no Instagram or Reddit item and a single TikTok item**: no public URL could be verified
  from the build environment. Pasting such links works through the adapters.
* **CSP is baseline only** (frame-ancestors, base-uri, form-action, object-src). A full script/frame
  allow-list for the five providers should be tested on real devices before a large launch.
* **Commercial limits**: Vercel Hobby is for non-commercial use; YouTube forbids charging to watch embedded
  videos and selling ads around its player; Reddit requires an agreement for commercial use.

## Asia: one continent, several different markets

| Market | Fit with SCROLL's five platforms | Notes |
|---|---|---|
| Japan | Good: YouTube, X, Instagram, TikTok are all large | LINE is the largest network and has no public embed for feeds; sharing to LINE works through the native share sheet |
| South Korea | Good: YouTube and Instagram lead | KakaoTalk and Naver are not covered |
| Indonesia, Thailand, Vietnam, Philippines | Good: YouTube, TikTok, Instagram, Facebook | Facebook is not integrated yet (Meta oEmbed covers Facebook posts/videos: natural next adapter) |
| India | Partial: YouTube and Instagram are large | TikTok has been banned since 2020: hide or disable the TikTok source for the `in` region |
| Taiwan, Hong Kong, Singapore | Good | Traditional/Simplified Chinese UI available |
| Mainland China | Not addressable | YouTube, Instagram, X and Reddit are blocked; local platforms (Douyin, Bilibili, Weibo, Xiaohongshu) are not integrated and Vercel hosting is unreliable there |

Sources for platform usage: Pew Research "Social media platform use around the world" (Oct 2026) and
marketing aggregators (figures differ between sources; verify per country before quoting them).

## Raising the price before listing (cheapest first)

1. **Turn on analytics and collect 2–4 weeks of real usage** (visitors, returning visitors, saves, links
   added). A graph of real users is worth more than any feature.
2. **Native review of one or two languages** for the market you pitch (for example Japanese + Korean).
3. **A custom domain** and the contact/operator fields filled (`NEXT_PUBLIC_*` variables).
4. **A YouTube Data API key** so the feed shows fresh regional playlists instead of a static demo catalog.
5. **Short demo video and screenshots** in the target languages for the listing.

Where pre-revenue projects are listed (fees and policies change; check each site before listing): Flippa,
SideProjectors, IndieMaker, ExitBid. Acquire.com and Empire Flippers focus on businesses with revenue.

## Transfer checklist

| Asset | How it transfers |
|---|---|
| Source code | Transfer the GitHub repository (Settings → Transfer ownership) or deliver an archive |
| Hosting | Vercel project transfer to the buyer's team, or the buyer redeploys from the repository |
| Domain | Registrar transfer (none attached yet) |
| Database | Supabase project transfer (none configured yet) |
| API keys | Never transferred: the buyer creates their own (YouTube, Meta, Reddit) |
| Analytics history | Stays with the Vercel project; export before transfer |
| Brand | "SCROLL" is a common word: no trademark search has been done. A buyer may want to rename |
| Third-party licences | Open-source dependencies only (MIT/Apache/ISC families): see `package.json` |

## Environment variables added in this release

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_SITE_URL` | Public base URL for sitemap, canonical links and social previews |
| `NEXT_PUBLIC_OPERATOR_NAME` | Legal entity or person shown on the legal pages |
| `NEXT_PUBLIC_CONTACT_EMAIL` | Contact address shown on the legal pages |
