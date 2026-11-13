import { NextResponse } from "next/server";
import { listProviderInfo } from "@/lib/providers/registry";

/** GET /api/health → provider status (never exposes secrets, only whether they are configured). */
export async function GET() {
  return NextResponse.json({
    ok: true,
    time: new Date().toISOString(),
    supabaseConfigured: Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY),
    providers: listProviderInfo().map((p) => ({ id: p.id, status: p.status, capabilities: p.capabilities })),
  });
}
