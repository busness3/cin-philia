import { config } from "./config";
import type { MangaDetail, SearchResultItem } from "../types";

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${config.apiBaseUrl}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `Erreur ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function searchTitles(query: string): Promise<SearchResultItem[]> {
  const encoded = encodeURIComponent(query);
  const { results } = await apiFetch<{ results: SearchResultItem[] }>(`/api/search?q=${encoded}`);
  return results;
}

export async function fetchMangaDetail(mangadexId: string): Promise<MangaDetail> {
  return apiFetch<MangaDetail>(`/api/manga/${mangadexId}`);
}
