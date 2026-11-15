"use client";

import { useCallback, useEffect, useSyncExternalStore } from "react";
import { useUserStore } from "@/lib/store/user-store";
import { resolveLocale, resolveRegion, type Locale, type RegionId } from "./locales";
import { en, type MessageKey } from "./messages/en";
import { fr } from "./messages/fr";
import { hi } from "./messages/hi";
import { id } from "./messages/id";
import { ja } from "./messages/ja";
import { ko } from "./messages/ko";
import { th } from "./messages/th";
import { vi } from "./messages/vi";
import { zhHans } from "./messages/zh-Hans";
import { zhHant } from "./messages/zh-Hant";

export const MESSAGES: Record<Locale, Record<MessageKey, string>> = {
  en,
  fr,
  ja,
  ko,
  "zh-Hant": zhHant,
  "zh-Hans": zhHans,
  id,
  th,
  vi,
  hi,
};

export type TranslateVars = Record<string, string | number>;
export type Translate = (key: MessageKey, vars?: TranslateVars) => string;

export function translate(locale: Locale, key: MessageKey, vars?: TranslateVars): string {
  const template = MESSAGES[locale]?.[key] ?? en[key] ?? key;
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name: string) => (name in vars ? String(vars[name]) : match));
}

function subscribeLanguage(callback: () => void) {
  window.addEventListener("languagechange", callback);
  return () => window.removeEventListener("languagechange", callback);
}

/** Browser languages joined into one stable string (snapshots must be primitives). */
function languagesSnapshot(): string {
  return (navigator.languages?.length ? navigator.languages : [navigator.language]).join(",");
}

const noopSubscribe = () => () => undefined;

/** False during server render and hydration, true afterwards: avoids hydration mismatches. */
export function useHydrated(): boolean {
  return useSyncExternalStore(
    noopSubscribe,
    () => true,
    () => false,
  );
}

function useBrowserLanguages(): string[] {
  const snapshot = useSyncExternalStore(subscribeLanguage, languagesSnapshot, () => "");
  return snapshot ? snapshot.split(",") : [];
}

/** Active UI locale: the explicit preference, else the first supported browser language, else English. */
export function useLocale(): Locale {
  const preference = useUserStore((s) => s.preferences.locale);
  const hydrated = useHydrated();
  const languages = useBrowserLanguages();
  if (!hydrated) return "en";
  return resolveLocale(preference, languages);
}

export function useRegion(): RegionId {
  const preference = useUserStore((s) => s.preferences.region);
  const locale = useLocale();
  const languages = useBrowserLanguages();
  return resolveRegion(preference, locale, languages);
}

export function useT(): Translate {
  const locale = useLocale();
  return useCallback((key, vars) => translate(locale, key, vars), [locale]);
}

/** Keeps <html lang> in sync with the active locale (fonts, screen readers, hyphenation). */
export function LocaleEffects() {
  const locale = useLocale();
  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);
  return null;
}

export { LOCALES, LOCALE_NAMES, REGION_IDS } from "./locales";
export type { Locale, RegionId } from "./locales";
export type { MessageKey } from "./messages/en";
