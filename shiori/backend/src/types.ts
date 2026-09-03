export type MangaSource = "mangadex" | "anilist";

/** Résultat de recherche unifié, renvoyé par GET /api/search */
export interface SearchResultItem {
  source: MangaSource;
  /** id MangaDex (uuid) — présent seulement si source === "mangadex" */
  mangadexId?: string;
  /** id AniList (numérique) — présent seulement si source === "anilist" */
  anilistId?: number;
  title: string;
  coverUrl: string | null;
  year: number | null;
  status: string | null;
  /**
   * Un titre n'est "traçable" (suivi automatique des nouveaux chapitres
   * possible) que s'il est identifié sur MangaDex — voir README.
   */
  trackable: boolean;
}

/** Détail d'un titre MangaDex, renvoyé par GET /api/manga/:mangadexId */
export interface MangaDetail {
  mangadexId: string;
  title: string;
  coverUrl: string | null;
  description: string | null;
  status: string | null;
  latestChapter: ChapterSummary | null;
  recentChapters: ChapterSummary[];
}

export interface ChapterSummary {
  id: string;
  chapter: string | null;
  title: string | null;
  translatedLanguage: string;
  publishAt: string;
}
