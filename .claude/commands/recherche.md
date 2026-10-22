---
description: Fiche de recherche sourcée sur un sujet (obligatoire pour un sujet sensible)
argument-hint: <sujet> [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `perso`.

Délègue au sous-agent `chercheur` avec : sujet, client, date du jour. Ne
fais pas la recherche toi-même.

Vérifie la fiche dans `marketing/recherches/` (chaque fait sourcé,
ressources d'aide si sensible), puis présente : le sujet en 5 lignes,
l'angle recommandé, les pièges à éviter. Si l'idée est dans
`marketing/clients/{client}/idees.md`, passe son statut à 🔎 et ajoute le
chemin de la fiche.
