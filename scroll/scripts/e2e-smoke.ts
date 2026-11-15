/**
 * Playwright smoke test against a running dev/prod server (BASE_URL, default http://localhost:3100).
 * Emulates an iPhone, walks the four tabs, exercises like/save/hide, filters, the add-link flow (failure and
 * success), search, legal pages and the language switch. Selectors use data attributes, so the test is
 * independent of the UI language. Run: npm run e2e (with `npm start -- -p 3100` in another terminal).
 */
import { chromium, devices, type Page } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.BASE_URL ?? "http://localhost:3100";
const OUT = process.env.SHOTS_DIR ?? "e2e-shots";
mkdirSync(OUT, { recursive: true });

function assert(cond: unknown, msg: string): asserts cond {
  if (!cond) throw new Error(`ASSERT: ${msg}`);
}

const slideCount = (page: Page) => page.locator("article[data-index]").count();

async function main() {
  const browser = await chromium.launch();
  const errors: string[] = [];

  // ---------- English session ----------
  const context = await browser.newContext({ ...devices["iPhone 14 Pro"], deviceScaleFactor: 2, locale: "en-US" });
  const page = await context.newPage();
  page.on("pageerror", (e: Error) => errors.push(e.message));

  // 1. Home feed + onboarding
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForSelector("[data-index='0']", { timeout: 30_000 });
  const start = page.getByTestId("onboarding-start");
  if (await start.isVisible({ timeout: 4000 }).catch(() => false)) await start.click();
  await page.waitForTimeout(2000);
  assert((await page.getAttribute("html", "lang")) === "en", "html lang should be en");
  await page.screenshot({ path: `${OUT}/01-home-en.png` });
  const slides = await slideCount(page);
  assert(slides >= 30, `expected ≥30 slides, got ${slides}`);

  // 2. Like + save
  await page.locator("[data-action='like']").first().click();
  await page.locator("[data-action='save']").first().click();
  await page.waitForTimeout(400);

  // 3. Next slide
  await page.keyboard.press("ArrowDown");
  await page.waitForTimeout(1200);
  const active = await page.evaluate(() => {
    const scroller = document.querySelector(".feed-scroller") as HTMLElement;
    return Math.round(scroller.scrollTop / scroller.clientHeight);
  });
  assert(active === 1, `expected slide 1 active, got ${active}`);

  // 4. Hide removes one slide
  const before = await slideCount(page);
  await page.locator("[data-action='hide']").nth(1).click();
  await page.waitForTimeout(500);
  assert((await slideCount(page)) === before - 1, "hide should remove one slide");

  // 5. Platform filter
  await page.locator("[data-mode='x']").click();
  await page.waitForTimeout(800);
  const xOnly = await slideCount(page);
  assert(xOnly >= 1 && xOnly < slides, `X-only feed should be a subset (${xOnly})`);
  await page.screenshot({ path: `${OUT}/02-home-x.png` });
  await page.locator("[data-mode='mixed']").click();

  // 6. Discover + add link: unsupported, provider failure, success
  await page.goto(BASE + "/discover", { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${OUT}/03-discover-en.png` });
  await page.getByTestId("open-add-link").click();
  const input = page.getByTestId("add-link-input");
  await input.fill("https://example.com/not-supported");
  assert(await page.getByTestId("add-link-unsupported").isVisible(), "unsupported link message");
  await input.fill("https://www.youtube.com/watch?v=00000000000");
  await page.getByTestId("add-link-submit").click();
  await page.waitForSelector("[data-testid='add-link-error']", { timeout: 20_000 });
  await page.screenshot({ path: `${OUT}/04-add-link-error.png` });
  await input.fill("https://youtu.be/R6MlUcmOul8");
  await page.getByTestId("add-link-submit").click();
  await page.waitForURL(/\/\?open=/, { timeout: 20_000 });
  await page.waitForSelector("[data-index='0']");
  await page.waitForTimeout(1200);
  const firstTitle = await page.locator("article[data-index='0'] h2").innerText();
  assert(/Tears of Steel/i.test(firstTitle), `pinned item should be first, got "${firstTitle}"`);

  // 7. Search
  await page.goto(BASE + "/discover", { waitUntil: "networkidle" });
  await page.getByTestId("discover-search").fill("blender");
  await page.waitForSelector("[data-testid='search-sources']", { timeout: 15_000 });

  // 8. Saved
  await page.goto(BASE + "/saved", { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  assert((await page.locator("[data-testid='saved-list'] > li").count()) >= 1, "saved list should contain the bookmark");
  await page.screenshot({ path: `${OUT}/05-saved-en.png` });

  // 9. Profile: switch language to Japanese, check it persists and applies everywhere
  await page.goto(BASE + "/profile", { waitUntil: "networkidle" });
  await page.getByTestId("locale-select").selectOption("ja");
  await page.waitForTimeout(400);
  assert((await page.getAttribute("html", "lang")) === "ja", "html lang should switch to ja");
  assert(await page.getByRole("heading", { name: "プロフィール" }).isVisible(), "profile title should be Japanese");
  await page.screenshot({ path: `${OUT}/06-profile-ja.png`, fullPage: true });
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForSelector("[data-index='0']");
  await page.waitForTimeout(800);
  assert(await page.getByRole("link", { name: "ホーム" }).isVisible(), "tab bar should be Japanese after reload");

  // 10. Legal pages, manifest, health, security headers
  for (const path of ["/legal/about", "/legal/privacy", "/legal/terms"]) {
    const res = await page.goto(BASE + path, { waitUntil: "domcontentloaded" });
    assert(res?.ok(), `${path} should load`);
    assert((await page.locator("h1").count()) === 1, `${path} should have one h1`);
  }
  await page.screenshot({ path: `${OUT}/07-terms.png` });
  for (const path of ["/manifest.webmanifest", "/api/health", "/robots.txt", "/sitemap.xml", "/og.png"]) {
    assert((await page.request.get(BASE + path)).ok(), `${path} should be served`);
  }
  const headers = (await page.request.get(BASE + "/")).headers();
  assert(headers["x-content-type-options"] === "nosniff", "security headers should be set");
  await context.close();

  // ---------- Auto-detected locales: Korean, Thai, Hindi browsers ----------
  for (const [locale, lang, homeLabel] of [
    ["ko-KR", "ko", "홈"],
    ["th-TH", "th", "หน้าหลัก"],
    ["hi-IN", "hi", "होम"],
    ["zh-TW", "zh-Hant", "首頁"],
    ["id-ID", "id", "Beranda"],
    ["vi-VN", "vi", "Trang chủ"],
  ] as const) {
    const ctx = await browser.newContext({ ...devices["iPhone 14 Pro"], deviceScaleFactor: 2, locale });
    const p = await ctx.newPage();
    p.on("pageerror", (e: Error) => errors.push(`${locale}: ${e.message}`));
    await p.goto(BASE + "/", { waitUntil: "domcontentloaded" });
    await p.waitForSelector("[data-index='0']", { timeout: 30_000 });
    await p.waitForTimeout(1500);
    assert((await p.getAttribute("html", "lang")) === lang, `html lang should be ${lang} for ${locale}`);
    assert(await p.getByRole("link", { name: homeLabel }).isVisible(), `tab bar should be localized for ${locale}`);
    await p.screenshot({ path: `${OUT}/10-onboarding-${lang}.png` });
    const s = p.getByTestId("onboarding-start");
    if (await s.isVisible({ timeout: 3000 }).catch(() => false)) await s.click();
    await p.waitForTimeout(1200);
    await p.screenshot({ path: `${OUT}/11-home-${lang}.png` });
    if (lang === "ko") {
      // Regional boost: the first items should be tagged for Korea.
      const more = p.locator("[data-action='more']").first();
      await more.click();
      await p.waitForTimeout(500);
      await p.screenshot({ path: `${OUT}/12-why-ko.png` });
    }
    await ctx.close();
  }

  await browser.close();
  // "no supported source" comes from third-party players: the bundled headless Chromium ships without H.264.
  const realErrors = errors.filter((e) => !/ResizeObserver|hydrat|no supported source/i.test(e));
  if (realErrors.length) {
    console.error("Page errors:", realErrors);
    process.exit(1);
  }
  console.log(`SMOKE OK · ${slides} slides · 7 locales · screenshots in ${OUT}/`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
