# Colorimétrie — palettes des 12 sous-saisons (BROUILLON — à valider par Clea)

⚠️ **Statut : brouillon, une seule source, pas encore validé.** Les codes
hex ci-dessous ne sont plus une estimation à l'œil — ils ont été
**échantillonnés directement sur les pixels** de la charte de référence
« THE 12 SEASONS OF COLOR » que Clea a fournie (9 couleurs par
sous-saison, disposées en cercles). C'est donc fidèle à *cette image
précise*, mais ça reste **une seule source parmi plusieurs styles
possibles** — Clea a aussi fourni 7 autres chartes (inventyourimage,
Hello Hue, colorislab...) qui donnent des interprétations un peu
différentes de chaque sous-saison. Rien n'est validé tant que Clea n'a
pas comparé et tranché.

## Pourquoi ce document existe

Le document de référence de Clea (`typologie_pilier_physique.md`) explique
le *framework* colorimétrie (undertone, contraste, 4 saisons vs 12
sous-saisons) mais ne donne pas de table de codes couleur. Ce brouillon
comble le trou avec les couleurs des chartes fournies par Clea, en
attendant sa validation.

## Le modèle à 3 axes

Chaque saison de base a 3 traits caractéristiques, et chaque sous-saison
porte le nom du trait qui domine chez la personne :

| Saison de base | 3 traits | Sous-saisons |
|---|---|---|
| **Printemps** | Chaud · Clair · Éclatant | Light Spring, Warm Spring, Bright Spring |
| **Été** | Froid · Clair · Doux | Light Summer, Cool Summer, Soft Summer |
| **Automne** | Chaud · Profond · Mat | Soft Autumn, Warm Autumn, Dark Autumn |
| **Hiver** | Froid · Profond · Éclatant | Cool Winter, Dark Winter, Bright Winter |

Il y a donc **3 axes indépendants**, pas 2 :
1. **Température** (chaud/froid) — ce qu'on collecte déjà (`undertone`)
2. **Valeur / clarté** (clair/profond) — proche de ce qu'on collecte déjà (`niveau_contraste`)
3. **Éclat / intensité** (éclatant/mat-doux) — **on ne collecte rien là-dessus actuellement**

La sous-saison "pure" (Warm Spring, Cool Summer, Warm Autumn, Cool Winter)
correspond à une personne dont la température domine clairement — c'est
la seule que la V1 sait calculer avec les 2 inputs actuels. Les 2 autres
sous-saisons de chaque groupe (ex. Light Spring / Bright Spring) demandent
le 3e axe.

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
"douce" → sous-saison Light (Printemps/Été) ou Soft/Dark pour Automne/Hiver.
**Cette logique de mapping complète reste elle-même à construire et
valider une fois la question confirmée — pas implémentée maintenant.**

## Palettes par sous-saison (9 couleurs, échantillonnées sur la charte de Clea)

### Printemps
| Sous-saison | Couleurs |
|---|---|
| Light Spring | `#B294C6` `#BADEB8` `#F3B785` `#B5D7F2` `#FEF2C0` `#F4ABA5` `#FBF4E1` `#D7C5AD` `#A6835B` |
| Warm Spring *(= "Printemps" pur, utilisée en V1 4-saisons)* | `#357A7F` `#42875A` `#89B053` `#51B09C` `#FAE274` `#EC665B` `#FBFAE8` `#CB954F` `#99633F` |
| Bright Spring | `#7F53A2` `#C8D464` `#F9CD54` `#4B73B9` `#45925C` `#EA3627` `#D7C5AF` `#838383` `#5E3B28` |

### Été
| Sous-saison | Couleurs |
|---|---|
| Light Summer | `#4470B7` `#5CBFAA` `#DB448B` `#A999CA` `#D6EDDD` `#F2B7D3` `#FBF7C7` `#708AC7` `#A2A6A9` |
| Cool Summer *(= "Été" pur, utilisée en V1 4-saisons)* | `#4496BB` `#44958C` `#C34B71` `#8BBDE0` `#6EC1A7` `#D072A4` `#ADB9DF` `#FEFBDC` `#376098` |
| Soft Summer | `#566991` `#658385` `#955F6F` `#877A8C` `#54756A` `#DEA8B6` `#FBEFC5` `#D2CAC8` `#979B9E` |

### Automne
| Sous-saison | Couleurs |
|---|---|
| Soft Autumn | `#985542` `#D4A39E` `#ECC288` `#646176` `#7C99AB` `#99C8C2` `#656F54` `#706F50` `#969674` |
| Warm Autumn *(= "Automne" pur, utilisée en V1 4-saisons)* | `#B54A28` `#E48833` `#FBAE54` `#764524` `#C83B29` `#D05627` `#505831` `#4A7C41` `#617434` |
| Dark Autumn | `#49140E` `#913921` `#C97D4C` `#1F3C2A` `#4A7152` `#616229` `#15313F` `#285D6F` `#306FA4` |

### Hiver
| Sous-saison | Couleurs |
|---|---|
| Cool Winter *(= "Hiver" pur, utilisée en V1 4-saisons)* | `#31398E` `#6C3590` `#CC2C38` `#42926B` `#C54A78` `#F1C5DC` `#3859AA` `#878E94` `#1C2A4F` |
| Dark Winter | `#421E4A` `#7D162B` `#AC2D4B` `#112C27` `#317163` `#B44D82` `#1D4356` `#408DC1` `#296170` |
| Bright Winter | `#2F3492` `#4C9F75` `#DA4040` `#74C3EE` `#E9E858` `#E53892` `#E1F2FC` `#656366` `#000000` |

## Ce qui a changé côté code

- `palettes.py` → `PALETTES` (4 saisons de base, utilisées par la V1
  actuelle) et `SUBSEASON_PALETTES` (12 sous-saisons) mis à jour avec ces
  couleurs échantillonnées par pixel — beaucoup plus fidèles à l'image
  source que la première version (estimation à l'œil sur 2 images).
  Renommé "Deep Autumn"/"Deep Winter" en **"Dark Autumn"/"Dark Winter"**
  pour coller au nom exact utilisé sur la charte de Clea.
- Chaque sous-saison passe de 6 à **9 couleurs** (la charte source en donne 9).
- La logique de classification à 12 sous-saisons attend toujours la
  validation de la question du 3e axe ci-dessus — **pas branchée**.

## Ce qui reste à valider avec Clea

1. **Choisir la bonne source** — Clea a fourni 8 chartes différentes au
   total (dont 4 très détaillées : inventyourimage, Hello Hue, colorislab
   x2). Ce document n'utilise qu'une seule d'entre elles (« THE 12 SEASONS
   OF COLOR », la plus simple et régulière à échantillonner). Si Clea
   préfère le rendu d'une autre charte, ou veut un mélange, il faut le dire.
2. **Les codes hex ci-dessus** — fidèles à l'image choisie, mais à
   comparer à un vrai nuancier professionnel si Clea en a un.
3. **La question proposée pour le 3e axe** (éclat/intensité) — wording et pertinence.
4. **La logique de mapping complète** vers les 12 sous-saisons, une fois la question validée.
