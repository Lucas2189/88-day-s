import { NextResponse } from "next/server";
import { z } from "zod";
import { CATEGORY_IDS } from "@/lib/content/types";
import { parseContentUrl } from "@/lib/content/url";
import { resolveUrl } from "@/lib/providers/registry";
import { enforceRateLimit, errorFromProvider, jsonError } from "@/lib/server/http";

const bodySchema = z.object({
  url: z.string().min(8).max(2048),
  categories: z.array(z.enum(CATEGORY_IDS)).max(5).optional(),
});

/** POST /api/resolve { url, categories? } → { item } */
export async function POST(request: Request) {
  const limited = enforceRateLimit(request, "resolve", 20, 0.5);
  if (limited) return limited;

  let body: z.infer<typeof bodySchema>;
  try {
    body = bodySchema.parse(await request.json());
  } catch {
    return jsonError("bad_request", "Body must be { url: string, categories?: string[] }.", 400);
  }
  const parsed = parseContentUrl(body.url);
  if (!parsed) {
    return jsonError("invalid_url", "Unsupported or invalid URL. Paste a public YouTube, TikTok, Instagram, X or Reddit link.", 422);
  }
  try {
    const item = await resolveUrl(body.url, { categories: body.categories, origin: "user-submitted" });
    return NextResponse.json({ item }, { headers: { "cache-control": "private, max-age=300" } });
  } catch (err) {
    return errorFromProvider(err);
  }
}
