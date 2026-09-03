import { env } from "../config/env.js";
import type { ChapterSummary, MangaDetail, SearchResultItem } from "../types.js";

const BASE_URL = "https://api.mangadex.org";
const COVERS_URL = "https://uploads.mangadex.org/covers";

// MangaDex demande un User-Agent identifiable et un usage raisonnable de
// son API (pas de scraping massif) — voir https://api.mangadex.org/docs/2-limitations/
function headers(): Record<string, string> {
  return {
    "User-Agent": env.mangadexUserAgent,
    Accept: "application/json",
  };
}

async function mangadexFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { headers: headers() });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`MangaDex ${path} → ${res.status} ${res.statusText} ${body}`.trim());
  }
  return (await res.json()) as T;
}

interface MangaDexTitleMap {
  [lang: string]: string;
}

interface MangaDexCoverAttributes {
  fileName: string;
}

interface MangaDexRelationship {
  id: string;
  type: string;
  attributes?: MangaDexCoverAttributes;
}

interface MangaDexMangaAttributes {
  title: MangaDexTitleMap;
  altTitles: MangaDexTitleMap[];
  description: Record<string, string>;
  status: string;
  year: number | null;
}

interface MangaDexManga {
  id: string;
  attributes: MangaDexMangaAttributes;
  relationships: MangaDexRelationship[];
}

interface MangaDexListResponse<T> {
  data: T[];
  total: number;
}

interface MangaDexChapterAttributes {
  chapter: string | null;
  title: string | null;
  translatedLanguage: string;
  publishAt: string;
}

interface MangaDexChapter {
  id: string;
  attributes: MangaDexChapterAttributes;
}

function pickTitle(attributes: MangaDexMangaAttributes): string {
  const map = attributes.title ?? {};
  const preferred =
    map.fr ?? map.en ?? map["ja-ro"] ?? map.ja ?? Object.values(map)[0];
  if (preferred) return preferred;
  const alt = attributes.altTitles?.find((entry) => Object.values(entry)[0]);
  return alt ? Object.values(alt)[0] : "Titre inconnu";
}

function coverUrlFromRelationships(
  mangaId: string,
  relationships: MangaDexRelationship[],
): string | null {
  const cover = relationships.find((rel) => rel.type === "cover_art");
  if (!cover?.attributes?.fileName) return null;
  return `${COVERS_URL}/${mangaId}/${cover.attributes.fileName}.512.jpg`;
}

function toSearchResult(manga: MangaDexManga): SearchResultItem {
  return {
    source: "mangadex",
    mangadexId: manga.id,
    title: pickTitle(manga.attributes),
    coverUrl: coverUrlFromRelationships(manga.id, manga.relationships),
    year: manga.attributes.year ?? null,
    status: manga.attributes.status ?? null,
    trackable: true,
  };
}

function toChapterSummary(chapter: MangaDexChapter): ChapterSummary {
  return {
    id: chapter.id,
    chapter: chapter.attributes.chapter,
    title: chapter.attributes.title,
    translatedLanguage: chapter.attributes.translatedLanguage,
    publishAt: chapter.attributes.publishAt,
  };
}

const CONTENT_RATINGS = ["safe", "suggestive", "erotica"];

export async function searchMangaDex(query: string, limit = 15): Promise<SearchResultItem[]> {
  const params = new URLSearchParams();
  params.set("title", query);
  params.set("limit", String(limit));
  params.append("includes[]", "cover_art");
  params.append("order[relevance]", "desc");
  for (const rating of CONTENT_RATINGS) params.append("contentRating[]", rating);

  const res = await mangadexFetch<MangaDexListResponse<MangaDexManga>>(
    `/manga?${params.toString()}`,
  );
  return res.data.map(toSearchResult);
}

/**
 * Derniers chapitres publiés pour un titre, tous groupes de scan et
 * toutes langues confondus, triés du plus récent au plus ancien.
 * On ne filtre pas par langue : l'objectif est juste de détecter
 * qu'un nouveau chapitre existe quelque part, pas de le proposer à
 * la lecture (le lien de lecture reste celui saisi par l'utilisateur).
 */
export async function fetchMangaDexFeed(
  mangadexId: string,
  limit = 10,
): Promise<ChapterSummary[]> {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  params.append("order[chapter]", "desc");
  params.set("includeFutureUpdates", "0");
  for (const rating of CONTENT_RATINGS) params.append("contentRating[]", rating);

  const res = await mangadexFetch<MangaDexListResponse<MangaDexChapter>>(
    `/manga/${mangadexId}/feed?${params.toString()}`,
  );
  return res.data
    .map(toChapterSummary)
    .sort((a, b) => (chapterNumber(b.chapter) ?? -1) - (chapterNumber(a.chapter) ?? -1));
}

export function chapterNumber(chapter: string | null): number | null {
  if (chapter === null) return null;
  const parsed = Number.parseFloat(chapter);
  return Number.isNaN(parsed) ? null : parsed;
}

export async function fetchMangaDexDetail(mangadexId: string): Promise<MangaDetail> {
  const res = await mangadexFetch<{ data: MangaDexManga }>(
    `/manga/${mangadexId}?includes[]=cover_art`,
  );
  const manga = res.data;
  const recentChapters = await fetchMangaDexFeed(mangadexId, 10);
  const description = manga.attributes.description ?? {};

  return {
    mangadexId,
    title: pickTitle(manga.attributes),
    coverUrl: coverUrlFromRelationships(mangadexId, manga.relationships),
    description: description.fr ?? description.en ?? Object.values(description)[0] ?? null,
    status: manga.attributes.status ?? null,
    latestChapter: recentChapters[0] ?? null,
    recentChapters,
  };
}
