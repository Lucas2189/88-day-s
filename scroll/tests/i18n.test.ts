import { describe, expect, it } from "vitest";
import { MESSAGES, translate } from "@/lib/i18n";
import { LOCALES, detectLocale, matchLocale, resolveLocale, resolveRegion } from "@/lib/i18n/locales";
import { en, type MessageKey } from "@/lib/i18n/messages/en";

const keys = Object.keys(en) as MessageKey[];
const placeholders = (text: string) => (text.match(/\{\w+\}/g) ?? []).sort().join(",");

describe("message catalogs", () => {
  it.each(LOCALES)("%s has every key, no empty string and the same placeholders as English", (locale) => {
    const catalog = MESSAGES[locale];
    expect(Object.keys(catalog).sort()).toEqual([...keys].sort());
    for (const key of keys) {
      expect(catalog[key].trim().length, `${locale}:${key}`).toBeGreaterThan(0);
      expect(placeholders(catalog[key]), `${locale}:${key}`).toBe(placeholders(en[key]));
    }
  });

  it("interpolates variables and falls back to English", () => {
    expect(translate("en", "saved.all", { count: 3 })).toBe("All (3)");
    expect(translate("ja", "saved.all", { count: 3 })).toBe("すべて（3）");
    expect(translate("xx" as never, "nav.home")).toBe("Home");
  });
});

describe("locale detection", () => {
  it("maps browser tags to supported locales", () => {
    expect(matchLocale("ja-JP")).toBe("ja");
    expect(matchLocale("ko")).toBe("ko");
    expect(matchLocale("zh-TW")).toBe("zh-Hant");
    expect(matchLocale("zh-Hant-HK")).toBe("zh-Hant");
    expect(matchLocale("zh-CN")).toBe("zh-Hans");
    expect(matchLocale("in-ID")).toBe("id");
    expect(matchLocale("th-TH")).toBe("th");
    expect(matchLocale("de-DE")).toBeNull();
  });

  it("uses the first supported browser language, else English", () => {
    expect(detectLocale(["de-DE", "vi-VN", "en-US"])).toBe("vi");
    expect(detectLocale(["de-DE"])).toBe("en");
    expect(detectLocale(undefined)).toBe("en");
  });

  it("lets an explicit preference override the browser", () => {
    expect(resolveLocale("hi", ["ja-JP"])).toBe("hi");
    expect(resolveLocale("auto", ["ja-JP"])).toBe("ja");
  });

  it("derives the content region from the browser region, then the language", () => {
    expect(resolveRegion("auto", "en", ["en-IN"])).toBe("in");
    expect(resolveRegion("auto", "en", ["en-SG"])).toBe("sea");
    expect(resolveRegion("auto", "ja", ["ja"])).toBe("jp");
    expect(resolveRegion("auto", "en", ["en-US"])).toBe("global");
    expect(resolveRegion("kr", "en", ["en-US"])).toBe("kr");
  });
});
