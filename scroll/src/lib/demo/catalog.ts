import type { ContentItem } from "@/lib/content/types";
import raw from "./catalog.json";

interface Catalog {
  generatedAt: string;
  items: ContentItem[];
}

const catalog = raw as unknown as Catalog;

/** Demo items resolved from real public URLs by scripts/seed-demo.ts. Always labeled "Demo" in the UI. */
export const DEMO_ITEMS: ContentItem[] = catalog.items.map((it) => ({ ...it, origin: "demo" }));
export const DEMO_GENERATED_AT = catalog.generatedAt;
