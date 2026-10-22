---
description: Rapport de performance + plan 30 jours par l'Analyste
argument-hint: <chemin(s) des exports analytics> [période] [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Sans fichier d'export réel, **ne lance pas l'analyste** : demande les
exports (LinkedIn, Instagram, TikTok, YouTube, store, site). Aucune analyse
sans données.

Client : `client:` dans la demande, sinon `perso`.

Délègue au sous-agent `analyste` avec : chemins des exports, période,
client, date du jour.

Vérifie les deux fichiers dans `marketing/analytics/`, présente les 3
constats et les données manquantes. Si l'analyste propose une entrée
d'historique, ajoute-la à `marketing/clients/{client}/historique.md`.
