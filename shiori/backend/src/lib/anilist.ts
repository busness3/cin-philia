import type { SearchResultItem } from "../types.js";

const ANILIST_URL = "https://graphql.anilist.co";

const SEARCH_QUERY = `
query ($search: String, $perPage: Int) {
  Page(page: 1, perPage: $perPage) {
    media(search: $search, type: MANGA, sort: SEARCH_MATCH) {
      id
      title {
        romaji
        english
        native
      }
      coverImage {
        large
      }
      startDate {
        year
      }
      status
    }
  }
}`;

interface AniListMedia {
  id: number;
  title: { romaji: string | null; english: string | null; native: string | null };
  coverImage: { large: string | null } | null;
  startDate: { year: number | null } | null;
  status: string | null;
}

interface AniListResponse {
  data?: { Page: { media: AniListMedia[] } };
  errors?: Array<{ message: string }>;
}

function pickTitle(media: AniListMedia): string {
  return media.title.english ?? media.title.romaji ?? media.title.native ?? "Titre inconnu";
}

/**
 * Recherche complémentaire via AniList — utile pour les titres au
 * catalogue "éditorial" classique (manga publié officiellement) mal
 * indexés côté MangaDex (qui reste orienté scan/scanlation). Ces
 * résultats ne sont PAS traçables automatiquement : AniList ne fournit
 * pas de flux de chapitres exploitable pour la détection de nouveautés,
 * voir README.
 */
export async function searchAniList(query: string, perPage = 10): Promise<SearchResultItem[]> {
  const res = await fetch(ANILIST_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ query: SEARCH_QUERY, variables: { search: query, perPage } }),
  });

  if (!res.ok) {
    throw new Error(`AniList → ${res.status} ${res.statusText}`);
  }

  const json = (await res.json()) as AniListResponse;
  if (json.errors?.length) {
    throw new Error(`AniList → ${json.errors.map((e) => e.message).join(", ")}`);
  }

  const media = json.data?.Page.media ?? [];
  return media.map((m) => ({
    source: "anilist" as const,
    anilistId: m.id,
    title: pickTitle(m),
    coverUrl: m.coverImage?.large ?? null,
    year: m.startDate?.year ?? null,
    status: m.status ?? null,
    trackable: false,
  }));
}
