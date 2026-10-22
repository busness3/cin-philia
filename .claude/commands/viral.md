---
description: Série de contenus courts pensés pour la viralité — Veilleur → Chercheur → Créateur → Critique
argument-hint: <thème> [nombre de pièces, défaut 5] [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.
Tu routes et enchaînes, tu ne produis aucun livrable toi-même.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `perso`. Nombre de pièces :
celui demandé, sinon 5. Formats : ceux prioritaires dans `brand.md` du
client (TikTok pour `perso`), sinon Reel, TikTok, YouTube Short.

Sans thème, pioche dans `marketing/clients/{client}/idees.md` (statut 💡
ou 🔎) en priorité, et mets à jour les statuts au fil de l'eau.

Si `brand.md` définit des styles à tester (A, B, C…), répartis-les entre
les pièces pour que l'Analyste puisse comparer.

1. **Veilleur** → si aucune veille de moins de 7 jours n'existe dans
   `marketing/tendances/`, lance `veilleur` sur le thème. Sinon réutilise
   la plus récente.

1 bis. **Chercheur** → pour chaque pièce dont le sujet est sensible (liste
   dans `brand.md`), lance `chercheur` si aucune fiche n'existe dans
   `marketing/recherches/`. Pas de fiche → pas de pièce sur ce sujet.

2. **Créateur** → lance `createur` pour N pièces courtes, chacune bâtie sur
   une tendance ✅ ou ⚠️ adaptable de la veille (cite-la dans `sources`).
   Varie les tendances et les hooks d'une pièce à l'autre.

3. **Critique** → lance `critique` sur chaque pièce.
   - RETRAVAILLER → renvoie au `createur` avec les corrections, puis
     recritique. Deux allers-retours au plus par pièce.
   - BLOQUÉ → renvoie au `createur` avec la règle violée ; si la pièce
     reste bloquée, écarte-la.

4. **Résumé** — tableau : pièce · tendance · hook · note /35 · verdict.
   Classe-les de la plus prometteuse à la moins prometteuse et propose un
   ordre de publication. Suggère `/visuel` pour les pièces retenues et
   `/communaute` si un défi peut prolonger la série.
