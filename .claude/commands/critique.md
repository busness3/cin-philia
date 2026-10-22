---
description: Note virale + conformité marque d'un contenu par le Critique
argument-hint: <chemin du contenu dans marketing/content/>
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Sans chemin, prends la pièce la plus récente de `marketing/content/` et
dis laquelle.

Délègue au sous-agent `critique` avec : chemin de la pièce, client (lu dans
son frontmatter), date du jour.

Présente le verdict, la note /35 et les corrections. Si le verdict est
RETRAVAILLER ou BLOQUÉ, propose de renvoyer la pièce au `createur` avec les
corrections (nouvelle `version` du même fichier), puis de la recritiquer.
