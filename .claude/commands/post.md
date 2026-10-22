---
description: Une pièce de contenu par le Créateur
argument-hint: <format> <sujet ou chemin de brief> [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Si la demande (ou une pièce) relève d'une série qui a un skill dédié dans
`marketing/clients/{client}/brand.md`, invoque ce skill avec l'outil Skill
au lieu de déléguer au `createur`.

Demande : $ARGUMENTS

Formats acceptés : `linkedin-long`, `linkedin-carrousel`, `reel`, `tiktok`,
`youtube-long`, `youtube-short`, `instagram-post`. Si le format est absent
ou ambigu, demande-le.

Client : `client:` dans la demande, sinon `perso`. Cherche dans
`marketing/briefs/` le brief le plus récent qui correspond au sujet ; s'il
n'y en a pas, signale-le et continue sans.

Délègue au sous-agent `createur` avec : format, sujet, client, chemin du
brief (ou « aucun »), date du jour. Ne rédige pas le contenu toi-même.

Vérifie le fichier produit dans `marketing/content/` (frontmatter,
framework nommé, ≥ 2 hooks) puis présente les hooks et le chemin.
