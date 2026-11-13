import { NextResponse } from "next/server";
import { CATEGORY_IDS, PROVIDER_IDS, type CategoryId, type ProviderId } from "@/lib/content/types";
import { buildFeed } from "@/lib/server/feed";
import { enforceRateLimit } from "@/lib/server/http";

/** GET /api/feed?providers=youtube,tiktok&categories=music,gaming → FeedResponse */
export async function GET(request: Request) {
  const limited = enforceRateLimit(request, "feed", 60, 1);
  if (limited) return limited;
  const { searchParams } = new URL(request.url);
  const providers = (searchParams.get("providers") ?? "")
    .split(",")
    .filter((p): p is ProviderId => (PROVIDER_IDS as readonly string[]).includes(p));
  const categories = (searchParams.get("categories") ?? "")
    .split(",")
    .filter((c): c is CategoryId => (CATEGORY_IDS as readonly string[]).includes(c));
  const feed = await buildFeed({ providers, categories, includeDemo: searchParams.get("demo") !== "0" });
  return NextResponse.json(feed, { headers: { "cache-control": "public, max-age=60, stale-while-revalidate=300" } });
}
