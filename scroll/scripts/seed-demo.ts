/**
 * Resolves a curated list of REAL public URLs through the provider adapters and writes
 * src/lib/demo/catalog.json. Items are labeled origin="demo" in the UI. Run: npm run seed:demo
 * Only metadata returned by official oEmbed/API endpoints is persisted; no media is downloaded.
 */
import { writeFileSync } from "node:fs";
import { resolve as resolvePath } from "node:path";
import { resolveUrl } from "../src/lib/providers/registry";
import type { CategoryId, ContentItem } from "../src/lib/content/types";

interface Candidate {
  url: string;
  categories: CategoryId[];
}

const candidates: Candidate[] = [
  // Blender Foundation open movies (Creative Commons), verified reachable via oEmbed on 2026-11-13.
  { url: "https://www.youtube.com/watch?v=aqz-KE-bpKQ", categories: ["film", "art"] },
  { url: "https://www.youtube.com/watch?v=eRsGyueVLvQ", categories: ["film", "art"] },
  { url: "https://www.youtube.com/watch?v=R6MlUcmOul8", categories: ["film", "science"] },
  { url: "https://www.youtube.com/watch?v=WhWc3b3KhnY", categories: ["film", "animals"] },
  { url: "https://www.youtube.com/watch?v=mN0zPOpADL4", categories: ["film", "comedy"] },
  { url: "https://www.youtube.com/watch?v=Y-rmzh0PI3c", categories: ["film", "animals"] },
  { url: "https://www.youtube.com/watch?v=SkVqJ1SGeL0", categories: ["film", "comedy", "animals"] },
  { url: "https://www.youtube.com/watch?v=TLkA0RELQ1g", categories: ["film", "art"] },
  // Widely known public videos; titles verified through oEmbed on 2026-11-13.
  { url: "https://www.youtube.com/watch?v=jNQXAC9IVRw", categories: ["animals", "lifestyle"] }, // Me at the zoo
  { url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ", categories: ["music"] }, // Rick Astley
  { url: "https://www.youtube.com/watch?v=9bZkp7q19f0", categories: ["music", "comedy"] }, // PSY
  { url: "https://www.youtube.com/watch?v=4czjS9h4Fpg", categories: ["science"] }, // Perseverance landing
  { url: "https://www.youtube.com/watch?v=wbSwFU6tY1c", categories: ["science", "tech"] }, // Falcon Heavy
  { url: "https://www.youtube.com/watch?v=hY7m5jjJ9mM", categories: ["animals", "comedy"] }, // Cats compilation
  { url: "https://www.youtube.com/watch?v=J---aiyznGQ", categories: ["animals", "comedy"] }, // Keyboard Cat
  { url: "https://www.youtube.com/watch?v=txqiwrbYGrs", categories: ["comedy"] }, // David After Dentist
  { url: "https://www.youtube.com/watch?v=dMH0bHeiRNg", categories: ["comedy", "music"] }, // Evolution of Dance
  { url: "https://www.youtube.com/watch?v=xuCn8ux2gbs", categories: ["comedy", "education"] }, // history of the entire world
  { url: "https://www.youtube.com/watch?v=iG9CE55wbtY", categories: ["education"] }, // TED Ken Robinson
  { url: "https://www.youtube.com/watch?v=aircAruvnKk", categories: ["education", "tech"] }, // 3Blue1Brown
  { url: "https://www.youtube.com/watch?v=Yocja_N5s1I", categories: ["education"] }, // Crash Course
  { url: "https://www.youtube.com/watch?v=4I5Q3UXkGd0", categories: ["science", "education"] }, // Vsauce
  { url: "https://www.youtube.com/watch?v=MmB9b5njVbA", categories: ["gaming"] }, // Minecraft trailer
  { url: "https://www.youtube.com/watch?v=QkkoHAzjnUs", categories: ["gaming"] }, // GTA V trailer
  { url: "https://www.youtube.com/watch?v=zw47_q9wbBE", categories: ["gaming"] }, // Zelda BOTW
  { url: "https://www.youtube.com/watch?v=MnrJzXM7a6o", categories: ["tech"] }, // iPhone 2007
  { url: "https://www.youtube.com/watch?v=tF4DML7FIWk", categories: ["tech", "science"] }, // Boston Dynamics
  { url: "https://www.youtube.com/watch?v=VtvjbmoDx-I", categories: ["tech", "film"] }, // Apple 1984
  { url: "https://www.youtube.com/watch?v=FHtvDA0W34I", categories: ["sports", "science"] }, // Red Bull Stratos
  { url: "https://www.youtube.com/watch?v=3nbjhpcZ9_g", categories: ["sports"] }, // Usain Bolt
  { url: "https://www.youtube.com/watch?v=WxfZkMm3wcg", categories: ["travel", "lifestyle"] }, // Make It Count
  { url: "https://www.youtube.com/watch?v=XqZsoesa55w", categories: ["music", "animals"] }, // Baby Shark
  // TikTok: the sample video used in TikTok's own oEmbed documentation.
  { url: "https://www.tiktok.com/@scout2015/video/6718335390845095173", categories: ["comedy", "lifestyle"] },
  // X: the first post ever published on the platform.
  { url: "https://x.com/jack/status/20", categories: ["tech", "news"] },
];

async function main() {
  const items: ContentItem[] = [];
  for (const c of candidates) {
    try {
      const item = await resolveUrl(c.url, { categories: c.categories, origin: "demo" });
      items.push(item);
      console.log(`ok   ${item.provider.padEnd(9)} ${item.title.slice(0, 60)}`);
    } catch (err) {
      console.warn(`skip ${c.url} → ${(err as Error).message}`);
    }
  }
  const out = resolvePath(process.cwd(), "src/lib/demo/catalog.json");
  writeFileSync(out, JSON.stringify({ generatedAt: new Date().toISOString(), items }, null, 2));
  console.log(`\nWrote ${items.length} items to ${out}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
