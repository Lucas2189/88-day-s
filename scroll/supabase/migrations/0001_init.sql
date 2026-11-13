-- SCROLL · initial schema
-- Only metadata that providers expose through authorized endpoints is stored. No media files, ever.
-- Private user data is protected by Row Level Security (RLS).

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Reference data
-- ---------------------------------------------------------------------------
create table if not exists content_sources (
  id            text primary key,                 -- 'youtube' | 'tiktok' | 'instagram' | 'x' | 'reddit'
  name          text not null,
  docs_url      text,
  capabilities  jsonb not null default '{}'::jsonb,
  enabled       boolean not null default true
);

insert into content_sources (id, name, docs_url) values
  ('youtube',   'YouTube',   'https://developers.google.com/youtube/iframe_api_reference'),
  ('tiktok',    'TikTok',    'https://developers.tiktok.com/doc/embed-player'),
  ('instagram', 'Instagram', 'https://developers.facebook.com/docs/instagram-platform/oembed'),
  ('x',         'X',         'https://developer.x.com/en/docs/x-for-websites/oembed-api'),
  ('reddit',    'Reddit',    'https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki')
on conflict (id) do nothing;

-- Shared metadata cache (public, read-only for clients). Writes happen server-side with the service role.
create table if not exists content_items (
  id            text primary key,                 -- '<provider>:<external_id>'
  provider      text not null references content_sources(id),
  external_id   text not null,
  kind          text not null,
  url           text not null,
  title         text not null,
  description   text,
  author_name   text,
  author_url    text,
  thumbnail_url text,
  duration_seconds integer,
  published_at  timestamptz,
  categories    text[] not null default '{}',
  tags          text[] not null default '{}',
  embed         jsonb not null,
  origin        text not null default 'user-submitted',
  fetched_at    timestamptz not null default now(),
  expires_at    timestamptz,                      -- honour provider cache_age when present
  extras        jsonb
);
create index if not exists content_items_provider_idx on content_items (provider);
create index if not exists content_items_categories_idx on content_items using gin (categories);

-- ---------------------------------------------------------------------------
-- Per-user data (RLS: owner only)
-- ---------------------------------------------------------------------------
create table if not exists profiles (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at  timestamptz not null default now()
);

create table if not exists user_preferences (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  preferences jsonb not null default '{}'::jsonb,
  updated_at  timestamptz not null default now()
);

-- Connected provider accounts (only when a provider offers authorized user auth, e.g. YouTube OAuth later).
-- Tokens must be encrypted with Supabase Vault / pgsodium before storage; never store raw tokens.
create table if not exists connected_providers (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  provider      text not null references content_sources(id),
  external_user_id text,
  scopes        text[] not null default '{}',
  token_secret_id uuid,                            -- reference to vault.secrets
  connected_at  timestamptz not null default now(),
  unique (user_id, provider)
);

create table if not exists collections (
  id          uuid primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  name        text not null,
  emoji       text,
  created_at  timestamptz not null default now()
);
create index if not exists collections_user_idx on collections (user_id);

create table if not exists bookmarks (
  user_id        uuid not null references auth.users(id) on delete cascade,
  content_id     text not null,
  item           jsonb not null,                   -- snapshot of ContentItem metadata (no media)
  collection_ids uuid[] not null default '{}',
  note           text,
  created_at     timestamptz not null default now(),
  primary key (user_id, content_id)
);

create table if not exists hidden_content (
  user_id     uuid not null references auth.users(id) on delete cascade,
  target_type text not null check (target_type in ('content', 'author')),
  target      text not null,
  created_at  timestamptz not null default now(),
  primary key (user_id, target_type, target)
);

create table if not exists engagement_events (
  id            uuid primary key,
  user_id       uuid not null references auth.users(id) on delete cascade,
  content_id    text not null,
  provider      text not null,
  categories    text[] not null default '{}',
  author_key    text,
  event_type    text not null check (event_type in ('view','complete','skip','like','unlike','save','unsave','hide','share','open')),
  dwell_seconds real,
  created_at    timestamptz not null default now()
);
create index if not exists engagement_events_user_time_idx on engagement_events (user_id, created_at desc);

-- Materialised recommendation state per user (computed by a scheduled job or edge function later).
create table if not exists recommendations (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  affinity    jsonb not null default '{}'::jsonb,  -- { category: score }
  computed_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
alter table content_sources     enable row level security;
alter table content_items       enable row level security;
alter table profiles            enable row level security;
alter table user_preferences    enable row level security;
alter table connected_providers enable row level security;
alter table collections         enable row level security;
alter table bookmarks           enable row level security;
alter table hidden_content      enable row level security;
alter table engagement_events   enable row level security;
alter table recommendations     enable row level security;

create policy "sources are public"      on content_sources for select using (true);
create policy "content is public"       on content_items   for select using (true);

create policy "own profile"             on profiles            for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own preferences"         on user_preferences    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own connected providers" on connected_providers for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own collections"         on collections         for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own bookmarks"           on bookmarks           for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own hidden content"      on hidden_content      for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own events"              on engagement_events   for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own recommendations"     on recommendations     for select using (auth.uid() = user_id);

-- Auto-create a profile row on signup.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (user_id) values (new.id) on conflict do nothing;
  return new;
end; $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute procedure public.handle_new_user();
