import { Router } from "express";
import { searchMangaDex } from "../lib/mangadex.js";
import { searchAniList } from "../lib/anilist.js";
import type { SearchResultItem } from "../types.js";

export const searchRouter = Router();

/**
 * GET /api/search?q=...
 *
 * Recherche combinée MangaDex (source principale, seule source dont le
 * suivi automatique des chapitres est possible) + AniList (source
 * complémentaire pour les métadonnées éditoriales, résultats marqués
 * trackable: false — voir README).
 */
searchRouter.get("/", async (req, res) => {
  const q = String(req.query.q ?? "").trim();
  if (q.length < 2) {
    res.status(400).json({ error: "Le paramètre q doit contenir au moins 2 caractères." });
    return;
  }

  const [mangadexResult, anilistResult] = await Promise.allSettled([
    searchMangaDex(q),
    searchAniList(q),
  ]);

  const results: SearchResultItem[] = [];
  if (mangadexResult.status === "fulfilled") {
    results.push(...mangadexResult.value);
  }
  if (anilistResult.status === "fulfilled") {
    results.push(...anilistResult.value);
  }

  if (results.length === 0 && mangadexResult.status === "rejected" && anilistResult.status === "rejected") {
    console.error("Recherche échouée (MangaDex + AniList)", mangadexResult.reason, anilistResult.reason);
    res.status(502).json({ error: "Les services de recherche externes sont indisponibles." });
    return;
  }

  res.json({ results });
});
