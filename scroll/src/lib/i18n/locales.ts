export const LOCALES = ["en", "fr", "ja", "ko", "zh-Hant", "zh-Hans", "id", "th", "vi", "hi"] as const;
export type Locale = (typeof LOCALES)[number];
export type LocalePreference = "auto" | Locale;

/** Native names, shown as-is in the language picker. */
export const LOCALE_NAMES: Record<Locale, string> = {
  en: "English",
  fr: "Français",
  ja: "日本語",
  ko: "한국어",
  "zh-Hant": "繁體中文",
  "zh-Hans": "简体中文",
  id: "Bahasa Indonesia",
  th: "ไทย",
  vi: "Tiếng Việt",
  hi: "हिन्दी",
};

export const REGION_IDS = ["global", "jp", "kr", "in", "sea", "zh"] as const;
export type RegionId = (typeof REGION_IDS)[number];
export type RegionPreference = "auto" | RegionId;

const DEFAULT_REGION_BY_LOCALE: Record<Locale, RegionId> = {
  en: "global",
  fr: "global",
  ja: "jp",
  ko: "kr",
  "zh-Hant": "zh",
  "zh-Hans": "zh",
  id: "sea",
  th: "sea",
  vi: "sea",
  hi: "in",
};

/** Maps a BCP 47 tag (e.g. "zh-TW", "ja-JP") to a supported locale, or null. */
export function matchLocale(tag: string): Locale | null {
  const lower = tag.toLowerCase();
  if (lower.startsWith("zh")) {
    if (/hant|-tw|-hk|-mo/.test(lower)) return "zh-Hant";
    return "zh-Hans";
  }
  const base = lower.split("-")[0];
  if (base === "in") return "id"; // legacy Indonesian code
  if (base === "ms") return "id"; // Malay speakers get the closest available UI
  return (LOCALES as readonly string[]).includes(base) ? (base as Locale) : null;
}

export function detectLocale(languages: readonly string[] | undefined): Locale {
  for (const tag of languages ?? []) {
    const match = matchLocale(tag);
    if (match) return match;
  }
  return "en";
}

export function resolveLocale(preference: LocalePreference | undefined, languages: readonly string[] | undefined): Locale {
  if (preference && preference !== "auto") return preference;
  return detectLocale(languages);
}

/** Region from the explicit preference, else the browser region subtag, else the UI language. */
export function resolveRegion(preference: RegionPreference | undefined, locale: Locale, languages: readonly string[] | undefined): RegionId {
  if (preference && preference !== "auto") return preference;
  for (const tag of languages ?? []) {
    const region = tag.split("-").pop()?.toUpperCase();
    if (region === "JP") return "jp";
    if (region === "KR") return "kr";
    if (region === "IN") return "in";
    if (region && ["ID", "TH", "VN", "PH", "MY", "SG"].includes(region)) return "sea";
    if (region && ["TW", "HK", "MO"].includes(region)) return "zh";
  }
  return DEFAULT_REGION_BY_LOCALE[locale];
}
