import { supabaseAdmin } from "../lib/supabase.js";
import { chapterNumber, fetchMangaDexFeed } from "../lib/mangadex.js";
import { sendExpoPushNotifications, type PushMessage } from "../lib/expoPush.js";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface LibraryEntryRow {
  id: string;
  user_id: string;
  manga_id: string;
  title: string;
  cover_url: string | null;
}

interface MangaTitleRow {
  mangadex_id: string;
  title: string;
  last_known_chapter: number | null;
}

/**
 * Coeur du suivi des nouveautés : interrogé une fois par titre MangaDex
 * suivi par au moins un utilisateur en support "en_ligne" (jamais pour
 * les titres "papier", qui n'ont par définition pas de source à
 * surveiller). Compare le dernier chapitre connu (manga_titles) au flux
 * MangaDex actuel ; à la première nouveauté détectée, enregistre une
 * notification par utilisateur concerné et envoie un push Expo groupé.
 */
export async function checkNewChapters(): Promise<void> {
  const startedAt = Date.now();

  const { data: onlineEntries, error: entriesError } = await supabaseAdmin
    .from("library_entries")
    .select("id, user_id, manga_id, title, cover_url")
    .eq("support", "en_ligne")
    .not("manga_id", "is", null);

  if (entriesError) {
    console.error("[checkNewChapters] lecture library_entries impossible", entriesError);
    return;
  }

  const entries = (onlineEntries ?? []) as LibraryEntryRow[];
  if (entries.length === 0) {
    console.log("[checkNewChapters] aucun titre suivi en ligne, rien à faire");
    return;
  }

  const uniqueMangaIds = [...new Set(entries.map((e) => e.manga_id))];

  const { data: titleRows, error: titlesError } = await supabaseAdmin
    .from("manga_titles")
    .select("mangadex_id, title, last_known_chapter")
    .in("mangadex_id", uniqueMangaIds);

  if (titlesError) {
    console.error("[checkNewChapters] lecture manga_titles impossible", titlesError);
    return;
  }

  const titleById = new Map<string, MangaTitleRow>(
    (titleRows ?? []).map((t) => [t.mangadex_id, t as MangaTitleRow]),
  );

  const pushMessages: PushMessage[] = [];
  let titlesWithNewChapters = 0;

  for (const mangaId of uniqueMangaIds) {
    const titleRow = titleById.get(mangaId);
    if (!titleRow) {
      // Titre référencé par une bibliothèque mais jamais mis en cache :
      // ne devrait pas arriver (créé côté app à l'ajout), on l'ignore
      // plutôt que de deviner sa valeur de départ.
      continue;
    }

    try {
      const chapters = await fetchMangaDexFeed(mangaId, 15);
      const numericChapters = chapters
        .map((c) => chapterNumber(c.chapter))
        .filter((n): n is number => n !== null);

      if (numericChapters.length === 0) continue;

      const latest = Math.max(...numericChapters);
      const baseline = titleRow.last_known_chapter;

      // Premier passage sur ce titre : on amorce la référence sans
      // notifier (on ne sait pas ce que l'utilisateur a déjà lu avant
      // que le titre existe dans le cache).
      if (baseline === null) {
        await supabaseAdmin
          .from("manga_titles")
          .update({ last_known_chapter: latest, last_checked_at: new Date().toISOString() })
          .eq("mangadex_id", mangaId);
        continue;
      }

      if (latest > baseline) {
        const newCount = numericChapters.filter((n) => n > baseline).length;
        titlesWithNewChapters += 1;

        await supabaseAdmin
          .from("manga_titles")
          .update({ last_known_chapter: latest, last_checked_at: new Date().toISOString() })
          .eq("mangadex_id", mangaId);

        const concernedEntries = entries.filter((e) => e.manga_id === mangaId);

        const notificationRows = concernedEntries.map((entry) => ({
          user_id: entry.user_id,
          library_entry_id: entry.id,
          title_snapshot: entry.title,
          cover_snapshot: entry.cover_url,
          chapter_number: String(latest),
          new_chapters_count: newCount,
        }));

        const { error: notifError } = await supabaseAdmin
          .from("notifications")
          .insert(notificationRows);
        if (notifError) {
          console.error(`[checkNewChapters] insertion notifications échouée pour ${mangaId}`, notifError);
        }

        const userIds = [...new Set(concernedEntries.map((e) => e.user_id))];
        const { data: tokenRows } = await supabaseAdmin
          .from("push_tokens")
          .select("user_id, expo_push_token")
          .in("user_id", userIds);

        const body =
          newCount > 1
            ? `${newCount} nouveaux chapitres disponibles (jusqu'au chapitre ${latest})`
            : `Chapitre ${latest} disponible`;

        for (const token of tokenRows ?? []) {
          pushMessages.push({
            to: token.expo_push_token,
            title: entries.find((e) => e.manga_id === mangaId)?.title ?? titleRow.title,
            body,
            data: { mangaId, chapter: latest },
          });
        }
      } else {
        await supabaseAdmin
          .from("manga_titles")
          .update({ last_checked_at: new Date().toISOString() })
          .eq("mangadex_id", mangaId);
      }
    } catch (err) {
      console.error(`[checkNewChapters] échec MangaDex pour ${mangaId}`, err);
    }

    // Pause légère entre chaque appel pour rester raisonnable vis-à-vis
    // de l'API publique MangaDex (pas de rafale sur de grosses bibliothèques).
    await sleep(250);
  }

  if (pushMessages.length > 0) {
    await sendExpoPushNotifications(pushMessages);
  }

  const durationMs = Date.now() - startedAt;
  console.log(
    `[checkNewChapters] terminé en ${durationMs}ms — ${uniqueMangaIds.length} titres vérifiés, ${titlesWithNewChapters} avec nouveauté(s), ${pushMessages.length} push envoyés`,
  );
}
