# Plateforme marketing multi-agent — contrat partagé

Ce fichier est le **contrat** de la chaîne d'agents marketing. Il définit
l'architecture, le rôle de chaque agent, l'arborescence, les conventions de
fichiers et les règles transverses. Tout agent et toute slash command le lit
avant de produire.

Le contexte produit (vision, ton, confidentialité) est dans
[`../docs/CLAUDE.md`](../docs/CLAUDE.md). Les règles de marque opérationnelles
sont dans `clients/{client}/brand.md`.

## Architecture

```
                 Orchestrateur (Claude Code, session principale)
                 route · consolide · enchaîne — ne produit jamais lui-même
                                     │
   ┌──────────────┬──────────────┬───┴──────────┬──────────────┬──────────────┐
   │ stratege     │ createur     │ designer     │ presentateur │ analyste     │
   │ opus         │ sonnet       │ sonnet       │ sonnet       │ opus         │
   └──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘
       briefs/       content/     prompts-images/     decks/       analytics/

   Viralité :  veilleur (sonnet)   critique (opus)   communaute (sonnet)
                 tendances/          critiques/         communaute/
```

**Principe directeur** : l'orchestrateur n'écrit jamais le livrable lui-même.
Il route vers le bon sous-agent (`.claude/agents/*.md`), vérifie le résultat,
et enchaîne. Chaque fichier de sortie a un auteur unique, identifié dans son
frontmatter YAML.

## Roster

| Agent | Modèle | Rôle | Sortie |
|---|---|---|---|
| `stratege` | Opus | Niche, ICP, brief de campagne. Seul agent qui prend des décisions de positionnement. | `briefs/` |
| `createur` | Sonnet | Posts LinkedIn, carrousels, scripts Reels/TikTok, scripts YouTube. Toujours un framework copy nommé. | `content/` |
| `designer` | Sonnet | Prompts d'images prêts à l'emploi (Midjourney, Gemini/Imagen, Ideogram), déclinés par format. | `prompts-images/` |
| `presentateur` | Sonnet | Decks slide-par-slide auto-portants (markdown). | `decks/` |
| `analyste` | Opus | Rapport de performance + plan d'optimisation 30 jours, à partir d'exports réels. | `analytics/` |
| `veilleur` | Sonnet | Tendances (formats, sons, hooks) de la semaine, sourcées et filtrées par compatibilité marque. | `tendances/` |
| `critique` | Opus | Note virale /35 + conformité marque d'un contenu avant publication. Verdict PUBLIER / RETRAVAILLER / BLOQUÉ. | `critiques/` |
| `communaute` | Sonnet | Défi de marque, incitations UGC, réponses types aux commentaires, créateurs à contacter. | `communaute/` |

## Slash commands

| Commande | Agent(s) | Usage |
|---|---|---|
| `/brief <objectif>` | stratege | Brief de campagne complet |
| `/post <format> <sujet>` | createur | Une pièce de contenu |
| `/visuel <livrable ou sujet>` | designer | Pack de prompts images |
| `/analyse <fichier d'export>` | analyste | Rapport + plan 30j |
| `/deck <livrable ou sujet>` | presentateur | Deck |
| `/tendances [thème]` | veilleur | Veille de la semaine |
| `/critique <contenu>` | critique | Note virale + conformité avant publication |
| `/communaute <campagne>` | communaute | Faire circuler une campagne |
| `/viral <thème> [N]` | veilleur → createur → critique | Série de N contenus courts (défaut 5) |
| `/campagne <objectif>` | chaîne complète | veilleur → stratege → createur → critique → designer → presentateur → communaute |

Client par défaut : `reveal-you`. Pour un autre client, le préciser dans
l'argument (`client: <slug>`) et créer `clients/<slug>/`.

## Arborescence

```
marketing/
├── CLAUDE.md            ← ce contrat
├── _templates/          ← frontmatter de référence
├── clients/{client}/
│   ├── brand.md         ← règles de marque (BLOQUANTES)
│   ├── icp.md           ← cible(s)
│   └── historique.md    ← campagnes passées, apprentissages
├── briefs/              ← {date}-{client}-{campagne}.md
├── content/             ← {date}-{client}-{format}-{slug}.md
├── prompts-images/      ← {date}-{client}-{campagne}.md
├── decks/               ← {date}-{client}-{sujet}.md
├── analytics/           ← rapport-{client}-{période}.md · plan-optim-30j-{client}-{date}.md
├── tendances/           ← {date}-{client}-veille.md
├── critiques/           ← {date}-{client}-{slug-de-la-piece}.md
└── communaute/          ← {date}-{client}-{campagne}.md
```

`{date}` = `AAAA-MM-JJ`. `{slug}`, `{campagne}`, `{sujet}` en kebab-case sans
accents.

## Convention critique : frontmatter obligatoire

Chaque livrable commence par ce frontmatter (voir `_templates/frontmatter.md`) :

```yaml
---
client: reveal-you
campagne: lancement-v1
agent: createur
date: 2026-10-22
version: 1
statut: brouillon   # brouillon | a-valider | valide | publie
sources:            # livrables lus pour produire celui-ci
  - briefs/2026-10-22-reveal-you-lancement-v1.md
---
```

C'est ce qui rend la chaîne auditable et permet à un agent de relire ce
qu'un autre a produit avant lui. Une nouvelle itération d'un livrable
incrémente `version` dans le même fichier ; on ne crée pas de doublon.

## Règles transverses

1. **Lire avant de produire.** Tout agent lit `clients/{client}/brand.md`
   (et `icp.md` s'il existe) avant d'écrire quoi que ce soit.
2. **Les interdictions de marque sont bloquantes.** Un livrable qui en viole
   une n'est pas livré : l'agent le réécrit. Pour Reveal You, cela inclut
   le vocabulaire correctif et toute imagerie avant/après.
3. **Aucun chiffre inventé.** Pas de statistique, témoignage, nombre
   d'utilisateurs ou résultat de performance qui ne vient pas d'une source
   fournie. « Donnée manquante » est une réponse valide.
4. **Aucune promesse produit non livrée.** Ne présenter comme disponible que
   ce que `docs/CLAUDE.md` décrit comme fonctionnel en V1. La roadmap peut
   être évoquée comme « à venir », jamais comme acquise.
5. **Confidentialité.** Jamais de photo ou de donnée d'utilisatrice réelle
   dans un livrable marketing (finalité limitée, voir `docs/CLAUDE.md`).
6. **Séquentiel, pas parallèle.** Chaque étape d'une campagne dépend de la
   précédente : un agent à la fois, validation utilisatrice aux étapes
   critiques (après le brief, avant le deck).
7. **Viralité honnête.** Pas de faux comptes, d'achat d'abonnés ou de vues,
   de groupes d'engagement, de faux avis, de concours sans vrai règlement,
   ni de partenariat non signalé. Aucun agent ne promet un nombre de vues.
8. **Français** pour tous les livrables, sauf les prompts d'images (anglais,
   meilleur rendu des modèles) accompagnés d'une note en français.
