# Colorimétrie — palettes des 12 sous-saisons (✅ validée par Clea pour la V1)

✅ **Statut : validée par Clea pour la V1** (« Pour une première version
c'est bien »). Les codes hex ci-dessous ne sont pas une estimation à
l'œil — ils ont été **échantillonnés directement sur les pixels** de la
charte de référence « THE 12 SEASONS OF COLOR » que Clea a fournie (9
couleurs par sous-saison, disposées en cercles).

Reste ouvert pour une itération future, **non bloquant pour la V1** :
Clea a aussi fourni 7 autres chartes (inventyourimage, Hello Hue,
colorislab...) avec des rendus plus proches de l'identité de marque pour
certaines sous-saisons (voir la section "Autres sources explorées"
ci-dessous), mais colorislab distingue "True Autumn" / "Warm Autumn"
comme 2 palettes différentes alors que notre modèle n'en a qu'une — pas
tranché, à reprendre si Clea veut affiner la palette plus tard.

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

## Autres sources explorées (non retenues pour la V1)

Clea a fourni 4 chartes supplémentaires dans un style plus élégant, plus
proche de l'identité de marque (colorislab × 3, Hello Hue × 1),
échantillonnées par pixel elles aussi, à titre de référence pour une
itération future :

| Sous-saison | Source | Couleurs (échantillon) |
|---|---|---|
| True Autumn | colorislab (54 couleurs) | `#F4DCB0` `#F5A923` `#EF8D04` `#D46F03` `#9D4B03` `#7A6315` `#3B3006` `#CC110E` `#093534` |
| Warm Autumn | colorislab (54 couleurs) | `#3E1302` `#AB5115` `#F8D28E` `#ED480F` `#EBA603` `#4A8A16` `#0B5652` `#07527C` `#703860` |
| True Summer | colorislab, Sister Seasons (36 couleurs) | `#605F65` `#A6747F` `#D87391` `#F3CFD3` `#72A6BE` `#A5BAD2` `#707EA1` `#8A7A9E` `#D2A3BC` |
| Soft Summer | colorislab, Sister Seasons (36 couleurs) | `#554045` `#B6606F` `#D69EA7` `#72A1AB` `#7CA1B1` `#6A89A5` `#817599` `#965B6F` |
| Soft Autumn (alt.) | colorislab, Sister Seasons (36 couleurs) | `#51342B` `#E5CBB4` `#B6505D` `#6B8A87` `#316976` `#507184` `#566481` `#8B5764` |

**Point non tranché, non bloquant pour la V1 :** colorislab distingue
« True Autumn » et « Warm Autumn » comme 2 palettes différentes, alors
que notre modèle n'a qu'un seul nœud "pure" pour l'Automne. Si Clea veut
utiliser une de ces couleurs plus tard, il faudra d'abord clarifier
laquelle correspond à ce que l'app appelle "Automne".

## Statut

✅ **Validé par Clea pour la V1** (« Pour une première version c'est
bien ») — les palettes de `palettes.py` (issues de « THE 12 SEASONS OF
COLOR ») sont la version de production. Reste ouvert, non bloquant, pour
une itération future :

1. Comparer les sources colorislab/Hello Hue ci-dessus si Clea veut
   affiner la palette plus tard, en tranchant d'abord le point
   True/Warm Autumn.
2. **La question proposée pour le 3e axe** (éclat/intensité) — wording et pertinence.
3. **La logique de mapping complète** vers les 12 sous-saisons, une fois la question validée.
