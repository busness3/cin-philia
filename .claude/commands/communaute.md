---
description: Défi de marque, UGC, réponses types et créateurs par le Community manager
argument-hint: <campagne ou chemin de brief> [sections] [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `perso`. Retrouve le brief
de la campagne dans `marketing/briefs/` et la dernière veille dans
`marketing/tendances/`.

Délègue au sous-agent `communaute` avec : campagne, brief, veille, sections
demandées (toutes par défaut), client, date du jour.

Vérifie le fichier dans `marketing/communaute/` puis présente le défi, le
hashtag et les décisions qui attendent l'utilisatrice.
