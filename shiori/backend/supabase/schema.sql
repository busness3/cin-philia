-- Schéma Supabase — Cin Philia Manga Tracker
-- À exécuter dans l'éditeur SQL du projet Supabase (une seule fois).
-- Utilise auth.users (fourni par Supabase Auth) pour les comptes.

create extension if not exists "pgcrypto";

-- ============================================================
-- manga_titles : cache partagé des titres suivis, un par manga
-- MangaDex. Sert de référence pour le job de suivi (un seul
-- appel MangaDex par titre, peu importe combien d'utilisateurs
-- le suivent).
-- ============================================================
create table if not exists public.manga_titles (
  mangadex_id uuid primary key,
  title text not null,
  cover_url text,
  last_known_chapter numeric,
  last_checked_at timestamptz,
  created_at timestamptz not null default now()
);

alter table public.manga_titles enable row level security;

-- Lecture publique (nécessaire pour afficher les fiches côté app).
create policy "manga_titles_select_all"
  on public.manga_titles for select
  to authenticated
  using (true);

-- Un utilisateur authentifié peut créer l'entrée de cache la première
-- fois qu'il ajoute un titre à sa bibliothèque (upsert "on conflict do
-- nothing" côté client). Il ne peut PAS la modifier ensuite : seule la
-- clé service_role (utilisée par le job cron du backend) met à jour
-- last_known_chapter, pour éviter qu'un client ne fausse le suivi.
create policy "manga_titles_insert_authenticated"
  on public.manga_titles for insert
  to authenticated
  with check (true);

-- ============================================================
-- library_entries : bibliothèque personnelle de chaque utilisateur
-- ============================================================
create table if not exists public.library_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  manga_id uuid references public.manga_titles(mangadex_id) on delete set null,
  anilist_id integer,
  source text not null default 'mangadex' check (source in ('mangadex', 'anilist', 'manuel')),
  title text not null,
  cover_url text,
  current_chapter text,
  reading_url text,
  support text not null default 'en_ligne' check (support in ('papier', 'en_ligne')),
  status text not null default 'en_cours' check (status in ('a_lire', 'en_cours', 'a_jour', 'en_pause', 'termine', 'abandonne')),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists library_entries_user_id_idx on public.library_entries (user_id);
create index if not exists library_entries_manga_id_idx on public.library_entries (manga_id) where support = 'en_ligne';

alter table public.library_entries enable row level security;

create policy "library_entries_owner_select"
  on public.library_entries for select
  to authenticated
  using (auth.uid() = user_id);

create policy "library_entries_owner_insert"
  on public.library_entries for insert
  to authenticated
  with check (auth.uid() = user_id);

create policy "library_entries_owner_update"
  on public.library_entries for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "library_entries_owner_delete"
  on public.library_entries for delete
  to authenticated
  using (auth.uid() = user_id);

-- updated_at automatique
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists library_entries_set_updated_at on public.library_entries;
create trigger library_entries_set_updated_at
  before update on public.library_entries
  for each row execute function public.set_updated_at();

-- ============================================================
-- notifications : nouveaux chapitres détectés par le job cron
-- ============================================================
create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  library_entry_id uuid not null references public.library_entries(id) on delete cascade,
  title_snapshot text not null,
  cover_snapshot text,
  chapter_number text,
  new_chapters_count integer not null default 1,
  read boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists notifications_user_id_idx on public.notifications (user_id, created_at desc);

alter table public.notifications enable row level security;

create policy "notifications_owner_select"
  on public.notifications for select
  to authenticated
  using (auth.uid() = user_id);

create policy "notifications_owner_update"
  on public.notifications for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- L'insertion se fait uniquement depuis le backend (clé service_role,
-- qui contourne RLS) au moment où le job cron détecte un nouveau
-- chapitre : pas de policy insert pour "authenticated" ici, volontairement.

-- ============================================================
-- push_tokens : jetons Expo Push par utilisateur/appareil
-- ============================================================
create table if not exists public.push_tokens (
  user_id uuid not null references auth.users(id) on delete cascade,
  expo_push_token text not null,
  created_at timestamptz not null default now(),
  primary key (user_id, expo_push_token)
);

alter table public.push_tokens enable row level security;

create policy "push_tokens_owner_all"
  on public.push_tokens for all
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
