---
description: Brief de campagne complet par le Stratège
argument-hint: <objectif de campagne> [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Client : celui précisé par `client:` dans la demande, sinon `reveal-you`.
S'il n'existe pas de `marketing/clients/{client}/brand.md`, arrête-toi et
demande les règles de marque avant de lancer quoi que ce soit.

Délègue au sous-agent `stratege` avec : la demande, le client, la date du
jour. Ne rédige pas le brief toi-même.

Quand il a fini, vérifie que le fichier existe dans `marketing/briefs/` avec
son frontmatter complet, puis résume à l'utilisatrice : message clé, 3
angles, questions ouvertes. Demande-lui de valider ou d'ajuster.
