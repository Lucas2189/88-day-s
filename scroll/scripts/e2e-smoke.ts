/**
 * Playwright smoke test against a running dev/prod server (BASE_URL, default http://localhost:3100).
 * Emulates an iPhone, walks the four tabs, exercises like/save/hide, the add-link flow and provider failure.
 * Run: npm run e2e  (requires `npm run dev -- -p 3100` or `npm start` in another terminal)
 */
import { chromium, devices } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.BASE_URL ?? "http://localhost:3100";
const OUT = process.env.SHOTS_DIR ?? "e2e-shots";
mkdirSync(OUT, { recursive: true });

function assert(cond: unknown, msg: string): asserts cond {
  if (!cond) throw new Error(`ASSERT: ${msg}`);
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ ...devices["iPhone 14 Pro"], deviceScaleFactor: 2, locale: "en-US" });
  const page = await context.newPage();
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  // 1. Home feed
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.waitForSelector("[data-index='0']", { timeout: 30_000 });
  // Onboarding sheet appears on first run
  const start = page.getByRole("button", { name: /Start/ });
  if (await start.isVisible({ timeout: 3000 }).catch(() => false)) {
    await page.getByRole("button", { name: "Music" }).click();
    await start.click();
  }
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/01-home.png` });
  const slides = await page.locator("article[data-index]").count();
  assert(slides >= 10, `expected ≥10 slides, got ${slides}`);

  // 2. Like + save + sound toggle
  await page.getByRole("button", { name: "Like" }).first().click();
  await page.getByRole("button", { name: "Save" }).first().click();
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${OUT}/02-home-liked-saved.png` });

  // 3. Swipe (scroll) to next slide → active index should advance
  await page.keyboard.press("ArrowDown");
  await page.waitForTimeout(1200);
  const active = await page.evaluate(() => {
    const scroller = document.querySelector(".feed-scroller") as HTMLElement;
    return Math.round(scroller.scrollTop / scroller.clientHeight);
  });
  assert(active === 1, `expected slide 1 active, got ${active}`);
  await page.screenshot({ path: `${OUT}/03-home-second.png` });

  // 4. Hide the current item → it disappears from the list
  const before = await page.locator("article[data-index]").count();
  await page.getByRole("button", { name: "Hide" }).nth(1).click();
  await page.waitForTimeout(500);
  const after = await page.locator("article[data-index]").count();
  assert(after === before - 1, `hide should remove one slide (${before} → ${after})`);

  // 5. Platform filter chip
  await page.getByRole("button", { name: "TikTok", exact: true }).first().click();
  await page.waitForTimeout(800);
  const tiktokOnly = await page.locator("article[data-index]").count();
  assert(tiktokOnly >= 1, "TikTok-only feed should have at least one item");
  await page.screenshot({ path: `${OUT}/04-home-tiktok.png` });
  await page.getByRole("button", { name: "For you" }).click();

  // 6. Discover + add link (success) + add link (unsupported)
  await page.goto(BASE + "/discover", { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${OUT}/05-discover.png` });
  await page.getByRole("button", { name: "Add link" }).click();
  const input = page.getByLabel("Public content URL");
  await input.fill("https://example.com/not-supported");
  assert(await page.getByText("Unsupported link").isVisible(), "unsupported link message");
  await input.fill("https://www.youtube.com/watch?v=00000000000");
  await page.getByRole("button", { name: "Add to my feed" }).click();
  await page.waitForSelector("text=/not found|cannot be embedded/i", { timeout: 20_000 });
  await page.screenshot({ path: `${OUT}/06-add-link-error.png` });
  await input.fill("https://youtu.be/R6MlUcmOul8");
  await page.getByRole("button", { name: "Add to my feed" }).click();
  await page.waitForURL(/\/\?open=/, { timeout: 20_000 });
  await page.waitForSelector("[data-index='0']");
  await page.waitForTimeout(1500);
  const firstTitle = await page.locator("article[data-index='0'] h2").innerText();
  assert(/Tears of Steel/i.test(firstTitle), `pinned item should be first, got "${firstTitle}"`);
  await page.screenshot({ path: `${OUT}/07-home-pinned-link.png` });

  // 7. Search
  await page.goto(BASE + "/discover", { waitUntil: "networkidle" });
  await page.getByLabel("Search").fill("blender");
  await page.waitForSelector("text=Catalog ✓", { timeout: 15_000 });
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${OUT}/08-search.png` });

  // 8. Saved
  await page.goto(BASE + "/saved", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  const savedCount = await page.locator("li").count();
  assert(savedCount >= 1, "saved list should contain the bookmark");
  await page.screenshot({ path: `${OUT}/09-saved.png` });

  // 9. Profile
  await page.goto(BASE + "/profile", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/10-profile.png`, fullPage: true });

  // 10. Manifest + health
  const manifest = await page.request.get(BASE + "/manifest.webmanifest");
  assert(manifest.ok(), "manifest should be served");
  const health = await page.request.get(BASE + "/api/health");
  assert(health.ok(), "health should be ok");

  await browser.close();
  // "no supported source" comes from third-party players: the bundled headless Chromium ships without H.264.
  const realErrors = errors.filter((e) => !/ResizeObserver|hydrat|no supported source/i.test(e));
  if (realErrors.length) {
    console.error("Page errors:", realErrors);
    process.exit(1);
  }
  console.log(`SMOKE OK · ${slides} slides · screenshots in ${OUT}/`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
