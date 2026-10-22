---
description: Pack de prompts images par le Designer
argument-hint: <chemin d'un livrable ou description du besoin> [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `reveal-you`. Si la demande cite
un livrable (contenu, brief, deck), passe son chemin ; sinon, cherche les
contenus récents de la même campagne dans `marketing/content/`.

Délègue au sous-agent `designer` avec : besoin, client, livrables sources,
date du jour. Ne rédige pas les prompts toi-même.

Vérifie le pack dans `marketing/prompts-images/` (frontmatter, 3 outils par
visuel, formats déclinés) puis présente le nombre de visuels et les alertes
de lisibilité.
