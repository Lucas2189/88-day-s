/** Renders public/icons/icon.svg to the PNG sizes the manifest needs (uses the bundled Chromium). */
import { chromium } from "playwright";
import { readFileSync, writeFileSync } from "node:fs";

async function main() {
  const svg = readFileSync("public/icons/icon.svg", "utf8");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 512, height: 512 }, deviceScaleFactor: 1 });
  const render = async (size: number, file: string, padding = 0) => {
    await page.setViewportSize({ width: size, height: size });
    await page.setContent(
      `<html><body style="margin:0;background:#000;display:grid;place-items:center;width:${size}px;height:${size}px"><img src="data:image/svg+xml;utf8,${encodeURIComponent(svg)}" style="width:${size - padding * 2}px;height:${size - padding * 2}px"/></body></html>`,
    );
    writeFileSync(file, await page.screenshot({ type: "png", clip: { x: 0, y: 0, width: size, height: size } }));
  };
  await render(192, "public/icons/icon-192.png");
  await render(512, "public/icons/icon-512.png");
  await render(512, "public/icons/icon-maskable-512.png", 64);
  await render(180, "public/icons/apple-touch-icon.png");
  // Social preview image (Open Graph / X card)
  await page.setViewportSize({ width: 1200, height: 630 });
  await page.setContent(
    `<html><body style="margin:0;background:#000;color:#fff;font-family:system-ui,-apple-system,Segoe UI,sans-serif;width:1200px;height:630px;display:flex;align-items:center;gap:64px;padding:0 96px;box-sizing:border-box"><img src="data:image/svg+xml;utf8,${encodeURIComponent(svg)}" style="width:260px;height:260px"/><div><div style="font-size:112px;font-weight:700;letter-spacing:-3px">SCROLL</div><div style="font-size:40px;opacity:.7;margin-top:12px">One app. One feed. Every social network.</div></div></body></html>`,
  );
  writeFileSync("public/og.png", await page.screenshot({ type: "png", clip: { x: 0, y: 0, width: 1200, height: 630 } }));
  await browser.close();
  console.log("icons written");
}
main();
