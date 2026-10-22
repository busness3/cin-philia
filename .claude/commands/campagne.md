---
description: Campagne complète — Stratège → Créateur → Designer → Présentateur
argument-hint: <objectif de campagne> [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.
Tu **routes, consolides et enchaînes** — tu ne produis aucun livrable
toi-même.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `reveal-you`. Date : aujourd'hui.

Déroule la chaîne **séquentiellement** (chaque étape lit les livrables de la
précédente) :

1. **Stratège** → `stratege` produit le brief dans `marketing/briefs/`.
   ⏸ **Validation** : présente message clé, angles et plan de contenu.
   Attends l'accord de l'utilisatrice (ou ses corrections, à repasser au
   stratège) avant de continuer.

2. **Créateur** → `createur` produit 3 à 5 pièces selon le plan de contenu
   du brief (une invocation par pièce, ou une invocation listant les pièces).
   Passe-lui le chemin du brief.

3. **Designer** → `designer` produit le pack visuel de la campagne à partir
   du brief + de toutes les pièces de l'étape 2.

4. **Présentateur** → `presentateur` consolide brief + contenus + pack en un
   deck de présentation de campagne.
   ⏸ **Validation** : présente le plan du deck et la liste des livrables.

5. **Clôture** — ajoute une entrée à `marketing/clients/{client}/historique.md`
   (format indiqué dans le fichier). Rappelle que l'Analyste interviendra à
   J+30 avec `/analyse <exports>`.

Entre chaque étape : vérifie que le livrable existe, que son frontmatter est
complet et que ses `sources` pointent vers l'étape précédente. Si un
livrable viole une interdiction de `brand.md`, renvoie-le à son agent avec
la règle violée — ne le corrige pas toi-même.

Résumé final : tableau étape · agent · fichier · statut.
