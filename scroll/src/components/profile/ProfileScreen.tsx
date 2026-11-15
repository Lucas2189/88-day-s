"use client";

import { useQuery } from "@tanstack/react-query";
import type { Session } from "@supabase/supabase-js";
import { ChevronRight, Download, LogIn, LogOut, RotateCcw, Trash2 } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { SourceStatusList } from "@/components/discover/SourceStatusList";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { PROVIDER_NAMES } from "@/components/ui/ProviderBadge";
import { useToast } from "@/components/ui/Toast";
import { trackEvent } from "@/lib/analytics";
import { api } from "@/lib/api/client";
import { CATEGORY_IDS, PROVIDER_IDS, type CategoryId } from "@/lib/content/types";
import { LOCALES, LOCALE_NAMES, REGION_IDS, useT } from "@/lib/i18n";
import type { LocalePreference, RegionPreference } from "@/lib/i18n/locales";
import { learnAffinity } from "@/lib/ranking/score";
import { useUserStore } from "@/lib/store/user-store";
import { getSupabaseBrowserClient, isSupabaseConfigured } from "@/lib/supabase/client";

function Section({ title, children, description }: { title: string; description?: string; children: ReactNode }) {
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
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-line bg-surface-2 px-4 py-3">
      <span>
        <span className="block text-sm font-medium">{label}</span>
        {hint && <span className="block text-xs text-fg-muted">{hint}</span>}
      </span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        onClick={() => onChange(!checked)}
        className={`relative h-7 w-12 shrink-0 rounded-full transition-colors ${checked ? "bg-white" : "bg-white/15"}`}
      >
        <span className={`absolute left-0.5 top-0.5 h-6 w-6 rounded-full transition-transform ${checked ? "translate-x-5 bg-black" : "bg-white"}`} />
      </button>
    </div>
  );
}

export function ProfileScreen() {
  const state = useUserStore();
  const { preferences, setPreferences, toggleInterest, toggleProvider, unhideAll, clearAll } = state;
  const { toast } = useToast();
  const t = useT();
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
  const stats: [string, number][] = [
    [t("profile.stat.saved"), Object.keys(state.bookmarks).length],
    [t("profile.stat.liked"), Object.keys(state.likes).length],
    [t("profile.stat.hidden"), Object.keys(state.hiddenContentIds).length + Object.keys(state.hiddenAuthors).length],
    [t("profile.stat.links"), Object.keys(state.submitted).length],
  ];

  const signIn = async () => {
    const sb = getSupabaseBrowserClient();
    if (!sb || !email.trim()) return;
    setSending(true);
    const { error } = await sb.auth.signInWithOtp({ email: email.trim(), options: { emailRedirectTo: `${window.location.origin}/auth/callback` } });
    setSending(false);
    if (error) toast(error.message, "error");
    else toast(t("profile.checkInbox"), "success");
  };

  const signOut = async () => {
    await getSupabaseBrowserClient()?.auth.signOut();
    toast(t("profile.signedOut"));
  };

  const exportData = () => {
    const blob = new Blob([JSON.stringify(useUserStore.getState(), null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `scroll-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const selectClass = "h-11 w-full appearance-none rounded-2xl border border-line bg-surface-2 px-4 text-sm outline-none focus:border-white/40";

  return (
    <div className="min-h-dvh pb-[calc(var(--tabbar-h)+var(--safe-bottom)+24px)]" style={{ paddingTop: "var(--safe-top)" }}>
      <header className="px-4 pt-4">
        <h1 className="font-display text-2xl font-semibold">{t("profile.title")}</h1>
        <div className="mt-4 grid grid-cols-4 gap-2 text-center">
          {stats.map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-line bg-surface-2 py-3">
              <p className="font-display text-xl font-semibold">{value}</p>
              <p className="truncate px-1 text-[11px] text-fg-muted">{label}</p>
            </div>
          ))}
        </div>
      </header>

      <Section title={t("profile.language")}>
        <select
          className={selectClass}
          aria-label={t("profile.language")}
          data-testid="locale-select"
          value={preferences.locale ?? "auto"}
          onChange={(e) => {
            setPreferences({ locale: e.target.value as LocalePreference });
            trackEvent("locale_changed", { locale: e.target.value });
          }}
        >
          <option value="auto">{t("profile.languageAuto")}</option>
          {LOCALES.map((l) => (
            <option key={l} value={l}>
              {LOCALE_NAMES[l]}
            </option>
          ))}
        </select>
      </Section>

      <Section title={t("profile.region")} description={t("profile.regionHint")}>
        <select
          className={selectClass}
          aria-label={t("profile.region")}
          data-testid="region-select"
          value={preferences.region ?? "auto"}
          onChange={(e) => setPreferences({ region: e.target.value as RegionPreference })}
        >
          <option value="auto">{t("region.auto")}</option>
          {REGION_IDS.map((r) => (
            <option key={r} value={r}>
              {t(`region.${r}`)}
            </option>
          ))}
        </select>
      </Section>

      <Section title={t("profile.account")} description={isSupabaseConfigured() ? t("profile.accountSync") : t("profile.accountLocal")}>
        {!isSupabaseConfigured() ? (
          <div className="rounded-2xl border border-dashed border-line p-4 text-xs text-fg-muted">{t("profile.accountSetup")}</div>
        ) : session ? (
          <div className="flex items-center justify-between rounded-2xl border border-line bg-surface-2 px-4 py-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{session.user.email}</p>
              <p className="text-xs text-fg-muted">{t("profile.synced")}</p>
            </div>
            <Button variant="secondary" size="sm" onClick={signOut}>
              <LogOut size={14} /> {t("profile.signOut")}
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
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" className="h-11 min-w-0 flex-1 rounded-full border border-line bg-surface-2 px-4 text-sm outline-none focus:border-white/40" aria-label={t("profile.email")} />
            <Button type="submit" loading={sending}>
              <LogIn size={16} /> {t("profile.magicLink")}
            </Button>
          </form>
        )}
      </Section>

      <Section title={t("profile.playback")}>
        <div className="space-y-2">
          <Toggle label={t("profile.autoplay")} hint={t("profile.autoplayHint")} checked={preferences.autoplay} onChange={(v) => setPreferences({ autoplay: v })} />
          <Toggle label={t("profile.startMuted")} hint={t("profile.startMutedHint")} checked={preferences.startMuted} onChange={(v) => setPreferences({ startMuted: v })} />
        </div>
      </Section>

      <Section title={t("profile.interests")}>
        <div className="flex flex-wrap gap-2">
          {CATEGORY_IDS.map((c) => (
            <Chip key={c} size="sm" active={preferences.interests.includes(c)} onClick={() => toggleInterest(c)}>
              {t(`category.${c}`)}
            </Chip>
          ))}
        </div>
      </Section>

      <Section title={t("profile.sources")} description={t("profile.sourcesHint")}>
        <div className="flex flex-wrap gap-2">
          {PROVIDER_IDS.map((p) => (
            <Chip key={p} size="sm" active={preferences.enabledProviders.includes(p)} onClick={() => toggleProvider(p)}>
              {PROVIDER_NAMES[p]}
            </Chip>
          ))}
        </div>
        <SourceStatusList providers={health.data?.providers ?? []} />
      </Section>

      <Section title={t("profile.ranking")} description={t("profile.rankingHint")}>
        <div className="rounded-2xl border border-line bg-surface-2 p-4 text-sm">
          <p className="text-fg-muted">{t("profile.rankingFormula")}</p>
          {topAffinities.length > 0 && (
            <ul className="mt-3 space-y-1.5">
              {topAffinities.map(([cat, v]) => (
                <li key={cat} className="flex items-center gap-2 text-xs">
                  <span className="w-28 shrink-0 truncate text-fg-muted">{t(`category.${cat}`)}</span>
                  <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
                    <span className={`block h-full ${v >= 0 ? "bg-white" : "bg-red-400"}`} style={{ width: `${Math.abs(v) * 100}%` }} />
                  </span>
                  <span className="w-10 text-right text-fg-faint">
                    {v >= 0 ? "+" : ""}
                    {v.toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="mt-3 text-xs text-fg-faint">{t("profile.events", { count: state.events.length })}</p>
        </div>
      </Section>

      <Section title={t("profile.data")}>
        <div className="space-y-2">
          <Button variant="secondary" className="w-full justify-start" onClick={exportData}>
            <Download size={16} /> {t("profile.export")}
          </Button>
          <Button
            variant="secondary"
            className="w-full justify-start"
            onClick={() => {
              unhideAll();
              toast(t("profile.hiddenRestored"));
            }}
          >
            <RotateCcw size={16} /> {t("profile.restoreHidden")}
          </Button>
          <Button
            variant="danger"
            className="w-full justify-start"
            onClick={() => {
              if (window.confirm(t("profile.clearConfirm"))) {
                clearAll();
                toast(t("profile.cleared"));
              }
            }}
          >
            <Trash2 size={16} /> {t("profile.clear")}
          </Button>
        </div>
      </Section>

      <Section title={t("profile.about")}>
        <ul className="overflow-hidden rounded-2xl border border-line bg-surface-2 text-sm">
          {(
            [
              ["/legal/about", t("profile.legal.about")],
              ["/legal/privacy", t("profile.legal.privacy")],
              ["/legal/terms", t("profile.legal.terms")],
            ] as const
          ).map(([href, label]) => (
            <li key={href} className="border-b border-line last:border-b-0">
              <Link href={href} className="flex items-center justify-between px-4 py-3">
                {label}
                <ChevronRight size={16} className="text-fg-faint" />
              </Link>
            </li>
          ))}
        </ul>
      </Section>

      <p className="mt-8 px-4 text-center text-[11px] text-fg-faint">SCROLL · {t("profile.footer")}</p>
    </div>
  );
}
