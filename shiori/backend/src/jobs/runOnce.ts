/**
 * Lance un seul passage du job de suivi, sans démarrer le serveur HTTP
 * ni le scheduler — utile en local (`npm run check-chapters`) ou comme
 * job planifié externe (cron système, GitHub Actions...) si on préfère
 * ne pas garder de process serveur toujours actif.
 */
import { checkNewChapters } from "./checkNewChapters.js";

checkNewChapters()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
