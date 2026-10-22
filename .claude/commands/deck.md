---
description: Deck slide-par-slide par le Présentateur
argument-hint: <chemin(s) des livrables sources ou sujet> [audience] [client: <slug>]
---

Tu es l'orchestrateur de la plateforme marketing. Lis `marketing/CLAUDE.md`.

Demande : $ARGUMENTS

Client : `client:` dans la demande, sinon `reveal-you`. Rassemble les
livrables sources : ceux cités, sinon les plus récents de la même campagne
dans `briefs/`, `content/`, `prompts-images/`, `analytics/`. Si l'audience
n'est pas précisée, déduis-la (interne, prospect, partenaire) et dis-le.

Délègue au sous-agent `presentateur` avec : sources, audience, client, date
du jour. Ne rédige pas le deck toi-même.

Vérifie le fichier dans `marketing/decks/` (frontmatter, structure nommée,
≥ 30 % de slides avec schéma) puis présente le plan des slides.
