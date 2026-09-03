export type Support = "papier" | "en_ligne";

export type Statut = "a_lire" | "en_cours" | "a_jour" | "en_pause" | "termine" | "abandonne";

export const STATUT_LABELS: Record<Statut, string> = {
  a_lire: "À lire",
  en_cours: "En cours",
  a_jour: "À jour",
  en_pause: "En pause",
  termine: "Terminé",
  abandonne: "Abandonné",
};

export const SUPPORT_LABELS: Record<Support, string> = {
  papier: "Papier",
  en_ligne: "En ligne",
};

export interface LibraryEntry {
  id: string;
  user_id: string;
  manga_id: string | null;
  anilist_id: number | null;
  source: "mangadex" | "anilist" | "manuel";
  title: string;
  cover_url: string | null;
  current_chapter: string | null;
  reading_url: string | null;
  support: Support;
  status: Statut;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AppNotification {
  id: string;
  user_id: string;
  library_entry_id: string;
  title_snapshot: string;
  cover_snapshot: string | null;
  chapter_number: string | null;
  new_chapters_count: number;
  read: boolean;
  created_at: string;
}

export type SearchSource = "mangadex" | "anilist";

export interface SearchResultItem {
  source: SearchSource;
  mangadexId?: string;
  anilistId?: number;
  title: string;
  coverUrl: string | null;
  year: number | null;
  status: string | null;
  trackable: boolean;
}

export interface ChapterSummary {
  id: string;
  chapter: string | null;
  title: string | null;
  translatedLanguage: string;
  publishAt: string;
}

export interface MangaDetail {
  mangadexId: string;
  title: string;
  coverUrl: string | null;
  description: string | null;
  status: string | null;
  latestChapter: ChapterSummary | null;
  recentChapters: ChapterSummary[];
}
