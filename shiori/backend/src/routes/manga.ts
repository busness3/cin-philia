import { Router } from "express";
import { fetchMangaDexDetail, fetchMangaDexFeed } from "../lib/mangadex.js";

export const mangaRouter = Router();

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function isValidMangadexId(id: string): boolean {
  return UUID_RE.test(id);
}

/**
 * GET /api/manga/:mangadexId
 *
 * Détail d'un titre MangaDex : utilisé au moment de l'ajout à la
 * bibliothèque (pour pré-remplir la fiche et amorcer manga_titles avec
 * le dernier chapitre connu, sans attendre le prochain passage du job
 * cron) et sur l'écran de fiche pour afficher les derniers chapitres
 * parus.
 */
mangaRouter.get("/:mangadexId", async (req, res) => {
  const { mangadexId } = req.params;
  if (!isValidMangadexId(mangadexId)) {
    res.status(400).json({ error: "Identifiant MangaDex invalide." });
    return;
  }

  try {
    const detail = await fetchMangaDexDetail(mangadexId);
    res.json(detail);
  } catch (err) {
    console.error(`Détail MangaDex ${mangadexId} indisponible`, err);
    res.status(502).json({ error: "MangaDex est indisponible pour le moment." });
  }
});

/** GET /api/manga/:mangadexId/chapters — derniers chapitres seuls. */
mangaRouter.get("/:mangadexId/chapters", async (req, res) => {
  const { mangadexId } = req.params;
  if (!isValidMangadexId(mangadexId)) {
    res.status(400).json({ error: "Identifiant MangaDex invalide." });
    return;
  }

  try {
    const chapters = await fetchMangaDexFeed(mangadexId, 20);
    res.json({ chapters });
  } catch (err) {
    console.error(`Flux de chapitres MangaDex ${mangadexId} indisponible`, err);
    res.status(502).json({ error: "MangaDex est indisponible pour le moment." });
  }
});
