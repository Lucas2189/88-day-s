import type { CategoryId, ContentItem, ProviderId } from "@/lib/content/types";

/**
 * Transparent MVP ranking. Every signal is collected INSIDE SCROLL; nothing is inferred from
 * external platforms. The formula is deliberately simple and documented in docs/architecture.md:
 *
 *   score = 1.0 * interestMatch        // explicit interests chosen by the user
 *         + 1.5 * learnedAffinity      // category affinity learned from in-app engagement
 *         + 0.6 * sourcePreference     // provider weight (0 when disabled)
 *         + 0.3 * recencyBoost         // newer publications get a small bump
 *         + 0.2 * explorationNoise     // deterministic per-session jitter for variety
 *         - 0.8 * seenPenalty          // already viewed in this session / recently
 *         - 1.2 * skipPenalty          // the user skipped this exact item quickly before
 *   and items that are hidden (or from hidden authors) are removed entirely.
 */

export type EngagementType = "view" | "complete" | "skip" | "like" | "unlike" | "save" | "unsave" | "hide" | "share" | "open";

export interface EngagementEvent {
  id: string;
  contentId: string;
  provider: ProviderId;
  categories: CategoryId[];
  authorKey?: string;
  type: EngagementType;
  /** Seconds the item was active in the viewport, when measurable. */
  dwellSeconds?: number;
  createdAt: string;
}

export interface RankingProfile {
  interests: CategoryId[];
  enabledProviders: ProviderId[];
  hiddenContentIds: Set<string>;
  hiddenAuthors: Set<string>;
  /** Learned per-category affinity in [-1, 1]. */
  affinity: Partial<Record<CategoryId, number>>;
  seenContentIds: Set<string>;
  skippedContentIds: Set<string>;
  /** Stable seed for exploration jitter so a session's order doesn't jump around on refetch. */
  seed: number;
}

/** Signal weights used to learn affinity from events (per category of the item). */
export const EVENT_WEIGHTS: Record<EngagementType, number> = {
  save: 3,
  like: 2,
  share: 2,
  complete: 1.5,
  open: 1,
  view: 0.4,
  skip: -1,
  unlike: -1.5,
  unsave: -2,
  hide: -3,
};

const HALF_LIFE_DAYS = 14;

/** Exponential time decay so old behaviour counts less. */
export function decayFactor(createdAt: string, now = Date.now()): number {
  const ageDays = Math.max(0, (now - new Date(createdAt).getTime()) / 86_400_000);
  return Math.pow(0.5, ageDays / HALF_LIFE_DAYS);
}

/**
 * Builds category affinities from raw events. Dwell time adds up to +1 for long views.
 * Result is squashed with tanh so a few strong signals cannot dominate forever.
 */
export function learnAffinity(events: EngagementEvent[], now = Date.now()): Partial<Record<CategoryId, number>> {
  const raw: Partial<Record<CategoryId, number>> = {};
  for (const ev of events) {
    let w = EVENT_WEIGHTS[ev.type] ?? 0;
    if (ev.type === "view" && ev.dwellSeconds !== undefined) {
      w += Math.min(1, ev.dwellSeconds / 20);
    }
    w *= decayFactor(ev.createdAt, now);
    for (const cat of ev.categories) raw[cat] = (raw[cat] ?? 0) + w;
  }
  const out: Partial<Record<CategoryId, number>> = {};
  for (const [cat, v] of Object.entries(raw) as [CategoryId, number][]) out[cat] = Math.tanh(v / 6);
  return out;
}

function hash(str: string, seed: number): number {
  let h = 2166136261 ^ seed;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h >>> 0) % 10_000) / 10_000;
}

export interface ScoredItem {
  item: ContentItem;
  score: number;
  reasons: string[];
}

export function scoreItem(item: ContentItem, profile: RankingProfile, now = Date.now()): ScoredItem | null {
  if (profile.hiddenContentIds.has(item.id)) return null;
  const authorKey = item.authorUrl ?? item.authorName;
  if (authorKey && profile.hiddenAuthors.has(authorKey)) return null;
  if (!profile.enabledProviders.includes(item.provider)) return null;

  const reasons: string[] = [];
  const cats = item.categories.length ? item.categories : (["lifestyle"] as CategoryId[]);

  const interestMatch = profile.interests.length ? cats.filter((c) => profile.interests.includes(c)).length / cats.length : 0.5;
  if (interestMatch > 0 && profile.interests.length) reasons.push("Matches your interests");

  const affinityValues = cats.map((c) => profile.affinity[c] ?? 0);
  const learnedAffinity = affinityValues.length ? affinityValues.reduce((a, b) => a + b, 0) / affinityValues.length : 0;
  if (learnedAffinity > 0.25) reasons.push("Similar to what you watched");
  if (learnedAffinity < -0.25) reasons.push("You tend to skip this");

  const sourcePreference = 1;

  let recencyBoost = 0;
  if (item.publishedAt) {
    const ageDays = (now - new Date(item.publishedAt).getTime()) / 86_400_000;
    recencyBoost = Math.max(0, 1 - ageDays / 30);
    if (recencyBoost > 0.5) reasons.push("Recently published");
  }

  const explorationNoise = hash(item.id, profile.seed);
  const seenPenalty = profile.seenContentIds.has(item.id) ? 1 : 0;
  const skipPenalty = profile.skippedContentIds.has(item.id) ? 1 : 0;

  const score =
    1.0 * interestMatch +
    1.5 * learnedAffinity +
    0.6 * sourcePreference +
    0.3 * recencyBoost +
    0.2 * explorationNoise -
    0.8 * seenPenalty -
    1.2 * skipPenalty;

  return { item, score, reasons };
}

export interface RankOptions {
  /** Avoid long runs of the same provider by applying a small diversity penalty. */
  diversify?: boolean;
}

export function rankItems(items: ContentItem[], profile: RankingProfile, opts: RankOptions = {}, now = Date.now()): ScoredItem[] {
  const scored = items.map((it) => scoreItem(it, profile, now)).filter((s): s is ScoredItem => s !== null);
  scored.sort((a, b) => b.score - a.score);
  if (!opts.diversify) return scored;

  // Greedy re-ranking: penalize picking the same provider/category as the previous pick.
  const out: ScoredItem[] = [];
  const pool = [...scored];
  let lastProvider: ProviderId | undefined;
  let lastCats: CategoryId[] = [];
  while (pool.length) {
    let bestIdx = 0;
    let bestVal = -Infinity;
    for (let i = 0; i < Math.min(pool.length, 8); i++) {
      const cand = pool[i];
      let val = cand.score;
      if (cand.item.provider === lastProvider) val -= 0.15;
      if (cand.item.categories.some((c) => lastCats.includes(c))) val -= 0.1;
      if (val > bestVal) {
        bestVal = val;
        bestIdx = i;
      }
    }
    const [pick] = pool.splice(bestIdx, 1);
    out.push(pick);
    lastProvider = pick.item.provider;
    lastCats = pick.item.categories;
  }
  return out;
}
