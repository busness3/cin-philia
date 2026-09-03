import cron from "node-cron";
import { env } from "../config/env.js";
import { checkNewChapters } from "./checkNewChapters.js";

let running = false;

export function startScheduler(): void {
  if (!cron.validate(env.chapterCheckCron)) {
    throw new Error(`Expression cron invalide : ${env.chapterCheckCron}`);
  }

  console.log(`[scheduler] job de suivi des chapitres planifié : "${env.chapterCheckCron}"`);

  cron.schedule(env.chapterCheckCron, async () => {
    if (running) {
      console.warn("[scheduler] passage précédent encore en cours, on saute ce tick");
      return;
    }
    running = true;
    try {
      await checkNewChapters();
    } catch (err) {
      console.error("[scheduler] échec inattendu du job", err);
    } finally {
      running = false;
    }
  });
}
