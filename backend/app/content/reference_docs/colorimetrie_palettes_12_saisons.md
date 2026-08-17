# Colorimétrie — palettes des 12 sous-saisons (BROUILLON — à valider par Clea)

⚠️ **Statut : brouillon, estimation visuelle, pas une extraction précise.**
Basé sur les 2 images de référence que Clea a fournies (chart français
"catalogue de tissus Izaure" + chart anglais "THE 12-SEASON COLOR
ANALYSIS"), complété par la méthode standard 12 saisons publiée dans le
secteur. Les codes hex sont des **estimations visuelles**, pas une
extraction pixel par pixel de l'image — à comparer aux vraies teintes
avant mise en prod.

## Le modèle à 3 axes (ce que les images révèlent)

Le chart anglais donne la clé de lecture : chaque saison de base a 3
traits caractéristiques, et chaque sous-saison porte le nom du trait qui
domine chez la personne :

| Saison de base | 3 traits | Sous-saisons |
|---|---|---|
| **Printemps** | Chaud · Clair · Éclatant | Light Spring, Warm Spring, Bright Spring |
| **Été** | Froid · Clair · Doux | Light Summer, Cool Summer, Soft Summer |
| **Automne** | Chaud · Profond · Mat | Soft Autumn, Warm Autumn, Deep Autumn |
| **Hiver** | Froid · Profond · Éclatant | Cool Winter, Deep Winter, Bright Winter |

Il y a donc **3 axes indépendants**, pas 2 :
1. **Température** (chaud/froid) — ce qu'on collecte déjà (`undertone`)
2. **Valeur / clarté** (clair/profond) — proche de ce qu'on collecte déjà (`niveau_contraste`)
3. **Éclat / intensité** (éclatant/mat-doux) — **on ne collecte rien là-dessus actuellement**

La sous-saison "pure" (Warm Spring, Cool Summer, Warm Autumn, Cool Winter)
correspond à une personne dont la température domine clairement. Les 2
autres sous-saisons de chaque groupe correspondent à une personne qui
penche vers l'axe clarté ou l'axe éclat.

## ⚠️ Ce qu'il manque pour classer réellement en 12 (pas juste en 4)

Avec seulement `undertone` + `niveau_contraste`, on peut déterminer la
**saison de base** (4 options — c'est ce que fait la V1 actuellement) mais
**pas la sous-saison** (12 options) : il manque le 3e axe (éclat/intensité).

**Proposition de question à ajouter au formulaire** (à valider/reformuler
par Clea avant implémentation — c'est un nouveau critère diagnostique, pas
juste une palette) :

> *"Tes couleurs naturelles (peau, yeux, cheveux) sont-elles plutôt vives
> et affirmées, ou douces et fondues l'une dans l'autre ?"*
> → Vive / Équilibrée / Douce

Avec ce 3e input, la logique de sous-saison deviendrait : "équilibrée" →
sous-saison pure (Warm Spring, Cool Summer...) ; "vive" → sous-saison
Bright (Printemps/Hiver) ou pousse vers Winter/Spring pour Automne/Été ;
"douce" → sous-saison Light (Printemps/Été) ou Soft/Deep pour Automne/Hiver.
**Cette logique de mapping complète reste elle-même à construire et
valider une fois la question confirmée — pas implémentée maintenant.**

## Palettes par sous-saison (estimation, 6 couleurs)

### Printemps
| Sous-saison | Couleurs |
|---|---|
| Light Spring | `#F6D9B0` `#F4B896` `#A9D8B8` `#C9E4A8` `#A8D4D8` `#B8CDE8` |
| Warm Spring *(= "Printemps" pur, utilisée en V1 4-saisons)* | `#E8895C` `#E0A030` `#C8AA3C` `#4E9E88` `#E86868` `#70A8A0` |
| Bright Spring | `#FF6B4A` `#FFC72C` `#2FA88C` `#3D7DD8` `#E8447A` `#7ED321` |

### Été
| Sous-saison | Couleurs |
|---|---|
| Light Summer | `#F0D9DC` `#E5CFE0` `#C8D8C0` `#B8CEDE` `#C7C4E0` `#A8B8C8` |
| Cool Summer *(= "Été" pur, utilisée en V1 4-saisons)* | `#9A4E6E` `#B85A8A` `#E0357A` `#4472A8` `#2C5C9E` `#5C90C8` |
| Soft Summer | `#B08890` `#9C8080` `#90A090` `#6E9E96` `#4E8C88` `#78889C` |

### Automne
| Sous-saison | Couleurs |
|---|---|
| Soft Autumn | `#B89878` `#A8A078` `#8CA084` `#6E9088` `#A87868` `#8C7868` |
| Warm Autumn *(= "Automne" pur, utilisée en V1 4-saisons)* | `#C1652F` `#D4A017` `#6B7A3A` `#B85C20` `#8C5A2C` `#A03828` |
| Deep Autumn | `#6F2C1C` `#7A3A10` `#2C4A2C` `#1C3C4A` `#4A1C3C` `#2C2418` |

### Hiver
| Sous-saison | Couleurs |
|---|---|
| Cool Winter *(= "Hiver" pur, utilisée en V1 4-saisons)* | `#7B2FA0` `#C8106E` `#1C4C9C` `#14807A` `#4C4C9C` `#E4E8EC` |
| Deep Winter | `#4A0E28` `#2C0A3C` `#0C2C4A` `#0C3C2C` `#1A1A1A` `#3C0A1A` |
| Bright Winter | `#E0146E` `#C8102E` `#0028A0` `#7B10A0` `#00A088` `#1A1A1A` |

## Ce qui a changé côté code

- `palettes.py` → `PALETTES` (4 saisons de base, utilisées par la V1
  actuelle) mises à jour pour utiliser les couleurs de la sous-saison
  "pure" ci-dessus (plus fidèles que le brouillon précédent).
- `palettes.py` → `SUBSEASON_PALETTES` (12 sous-saisons) ajoutées, prêtes
  à l'emploi, mais **pas encore branchées** dans `rules.py` — la logique
  de classification à 12 sous-saisons attend la validation de la question
  du 3e axe ci-dessus.

## Ce qui reste à valider avec Clea

1. Les codes hex ci-dessus (estimation visuelle, à comparer aux vraies images)
2. La question proposée pour le 3e axe (éclat/intensité) — wording et pertinence
3. La logique de mapping complète vers les 12 sous-saisons, une fois la question validée
