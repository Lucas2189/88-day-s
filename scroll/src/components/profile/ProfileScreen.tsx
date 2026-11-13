"use client";

import { useQuery } from "@tanstack/react-query";
import { Download, LogIn, LogOut, RotateCcw, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { useToast } from "@/components/ui/Toast";
import { api } from "@/lib/api/client";
import { CATEGORY_IDS, CATEGORY_LABELS, PROVIDER_IDS, type CategoryId } from "@/lib/content/types";
import { learnAffinity } from "@/lib/ranking/score";
import { useUserStore } from "@/lib/store/user-store";
import { getSupabaseBrowserClient, isSupabaseConfigured } from "@/lib/supabase/client";
import type { Session } from "@supabase/supabase-js";
import { SourceStatusList } from "@/components/discover/SourceStatusList";

function Section({ title, children, description }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <section className="mt-6 px-4">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-fg-faint">{title}</h2>
      {description && <p className="mt-1 text-sm text-fg-muted">{description}</p>}
      <div className="mt-3">{children}</div>
    </section>
  );
}

function Toggle({ label, hint, checked, onChange }: { label: string; hint?: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-4 rounded-2xl border border-line bg-surface-2 px-4 py-3">
      <span>
        <span className="block text-sm font-medium">{label}</span>
        {hint && <span className="block text-xs text-fg-muted">{hint}</span>}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-7 w-12 shrink-0 rounded-full transition-colors ${checked ? "bg-white" : "bg-white/15"}`}
      >
        <span className={`absolute top-0.5 h-6 w-6 rounded-full transition-transform ${checked ? "left-0.5 translate-x-5 bg-black" : "left-0.5 bg-white"}`} />
      </button>
    </label>
  );
}

export function ProfileScreen() {
  const state = useUserStore();
  const { preferences, setPreferences, toggleInterest, toggleProvider, unhideAll, clearAll } = state;
  const { toast } = useToast();
  const [session, setSession] = useState<Session | null>(null);
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const health = useQuery({ queryKey: ["feed", "profile"], queryFn: () => api.feed(), staleTime: 5 * 60_000 });

  useEffect(() => {
    const sb = getSupabaseBrowserClient();
    if (!sb) return;
    sb.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = sb.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);

  const affinity = useMemo(() => learnAffinity(state.events), [state.events]);
  const topAffinities = (Object.entries(affinity) as [CategoryId, number][]).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const stats = {
    saved: Object.keys(state.bookmarks).length,
    liked: Object.keys(state.likes).length,
    hidden: Object.keys(state.hiddenContentIds).length + Object.keys(state.hiddenAuthors).length,
    events: state.events.length,
    submitted: Object.keys(state.submitted).length,
  };

  const signIn = async () => {
    const sb = getSupabaseBrowserClient();
    if (!sb || !email.trim()) return;
    setSending(true);
    const { error } = await sb.auth.signInWithOtp({ email: email.trim(), options: { emailRedirectTo: `${window.location.origin}/auth/callback` } });
    setSending(false);
    if (error) toast(error.message, "error");
    else toast("Check your inbox for the sign-in link", "success");
  };

  const signOut = async () => {
    await getSupabaseBrowserClient()?.auth.signOut();
    toast("Signed out");
  };

  const exportData = () => {
    const blob = new Blob([JSON.stringify(useUserStore.getState(), null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `scroll-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="min-h-dvh pb-[calc(var(--tabbar-h)+var(--safe-bottom)+24px)]" style={{ paddingTop: "var(--safe-top)" }}>
      <header className="px-4 pt-4">
        <h1 className="font-display text-2xl font-semibold">Profile</h1>
        <div className="mt-4 grid grid-cols-4 gap-2 text-center">
          {[
            ["Saved", stats.saved],
            ["Liked", stats.liked],
            ["Hidden", stats.hidden],
            ["Links", stats.submitted],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-line bg-surface-2 py-3">
              <p className="font-display text-xl font-semibold">{value}</p>
              <p className="text-[11px] text-fg-muted">{label}</p>
            </div>
          ))}
        </div>
      </header>

      <Section title="Account" description={isSupabaseConfigured() ? "Sign in to sync bookmarks, collections and preferences across devices." : "Running in local mode: everything is stored on this device. Configure Supabase to enable sign-in and sync."}>
        {!isSupabaseConfigured() ? (
          <div className="rounded-2xl border border-dashed border-line p-4 text-xs text-fg-muted">
            Set <code className="text-fg">NEXT_PUBLIC_SUPABASE_URL</code> and <code className="text-fg">NEXT_PUBLIC_SUPABASE_ANON_KEY</code>, then run the migration in <code className="text-fg">supabase/migrations</code>.
          </div>
        ) : session ? (
          <div className="flex items-center justify-between rounded-2xl border border-line bg-surface-2 px-4 py-3">
            <div>
              <p className="text-sm font-medium">{session.user.email}</p>
              <p className="text-xs text-fg-muted">Synced to the cloud</p>
            </div>
            <Button variant="secondary" size="sm" onClick={signOut}>
              <LogOut size={14} /> Sign out
            </Button>
          </div>
        ) : (
          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              void signIn();
            }}
          >
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className="h-11 min-w-0 flex-1 rounded-full border border-line bg-surface-2 px-4 text-sm outline-none focus:border-white/40" aria-label="Email" />
            <Button type="submit" loading={sending}>
              <LogIn size={16} /> Magic link
            </Button>
          </form>
        )}
      </Section>

      <Section title="Playback">
        <div className="space-y-2">
          <Toggle label="Autoplay" hint="Start playing when a video becomes active (muted by default)." checked={preferences.autoplay} onChange={(v) => setPreferences({ autoplay: v })} />
          <Toggle label="Start muted" hint="Browsers require muted autoplay; tap the speaker to unmute." checked={preferences.startMuted} onChange={(v) => setPreferences({ startMuted: v })} />
        </div>
      </Section>

      <Section title="Interests">
        <div className="flex flex-wrap gap-2">
          {CATEGORY_IDS.map((c) => (
            <Chip key={c} size="sm" active={preferences.interests.includes(c)} onClick={() => toggleInterest(c)}>
              {CATEGORY_LABELS[c]}
            </Chip>
          ))}
        </div>
      </Section>

      <Section title="Sources" description="Disable a platform to remove it from every feed.">
        <div className="flex flex-wrap gap-2">
          {PROVIDER_IDS.map((p) => (
            <Chip key={p} size="sm" active={preferences.enabledProviders.includes(p)} onClick={() => toggleProvider(p)}>
              {PROVIDER_NAMES[p]}
            </Chip>
          ))}
        </div>
        <SourceStatusList providers={health.data?.providers ?? []} />
      </Section>

      <Section title="How your feed is ranked" description="All signals are collected inside SCROLL only. Nothing is read from your accounts on other platforms.">
        <div className="rounded-2xl border border-line bg-surface-2 p-4 text-sm">
          <p className="text-fg-muted">
            score = interests + 1.5 × learned affinity + source weight + 0.3 × recency + exploration − seen − skipped. Hidden content and authors are removed.
          </p>
          {topAffinities.length > 0 && (
            <ul className="mt-3 space-y-1.5">
              {topAffinities.map(([cat, v]) => (
                <li key={cat} className="flex items-center gap-2 text-xs">
                  <span className="w-28 shrink-0 text-fg-muted">{CATEGORY_LABELS[cat]}</span>
                  <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
                    <span className={`block h-full ${v >= 0 ? "bg-white" : "bg-red-400"}`} style={{ width: `${Math.abs(v) * 100}%` }} />
                  </span>
                  <span className="w-10 text-right text-fg-faint">{v >= 0 ? "+" : ""}{v.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-xs text-fg-faint">{stats.events} engagement events on this device (half-life 14 days).</p>
        </div>
      </Section>

      <Section title="Your data">
        <div className="space-y-2">
          <Button variant="secondary" className="w-full justify-start" onClick={exportData}>
            <Download size={16} /> Export my data (JSON)
          </Button>
          <Button
            variant="secondary"
            className="w-full justify-start"
            onClick={() => {
              unhideAll();
              toast("Hidden content restored");
            }}
          >
            <RotateCcw size={16} /> Restore hidden content
          </Button>
          <Button
            variant="danger"
            className="w-full justify-start"
            onClick={() => {
              if (window.confirm("Delete all local data (bookmarks, likes, history, links)? This cannot be undone.")) {
                clearAll();
                toast("Local data cleared");
              }
            }}
          >
            <Trash2 size={16} /> Clear local data
          </Button>
        </div>
      </Section>

      <p className="mt-8 px-4 text-center text-[11px] text-fg-faint">
        SCROLL MVP · Content is played through each platform&apos;s official embed and belongs to its creators. Platform names and logos are used for identification only.
      </p>
    </div>
  );
}
