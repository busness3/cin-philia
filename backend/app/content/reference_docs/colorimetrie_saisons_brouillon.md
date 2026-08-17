# Colorimétrie — table de correspondance saison (BROUILLON — à valider par Clea)

⚠️ **Statut : brouillon, pas une décision produit validée.** Contrairement
aux autres documents de ce dossier (fournis directement par Clea), ce
fichier a été rédigé par l'assistant technique pour débloquer la V1, en
s'appuyant sur la méthode de "color analysis" 4 saisons — un système
publié et largement utilisé dans l'industrie mode/beauté (pas propriétaire
à Reveal You, pas inventé de zéro). **Il doit être relu et corrigé par
Clea avant d'être considéré comme la vraie règle produit.**

## Pourquoi ce document existe

Le document de référence de Clea (`typologie_pilier_physique.md`) explique
le *framework* colorimétrie (undertone, contraste, 4 saisons vs 12
sous-saisons) mais ne donne pas la table de correspondance elle-même —
signalé comme point ouvert dans le document source. Pour avoir une V1
testable de bout en bout, ce brouillon comble le trou avec la logique
standard du secteur, en attendant la validation ou correction de Clea.

## Portée retenue pour la V1

**4 saisons de base uniquement** (pas de 12 sous-saisons) — cohérent avec
la discipline MVP : moins précis, mais calculable de façon fiable à partir
des 3 inputs déclaratifs qu'on collecte (undertone, contraste, couleur de
cheveux en texte libre). Les 12 sous-saisons demanderaient des signaux
supplémentaires (ex. couleur des yeux précise, test du drapé) qu'on ne
collecte pas en V1.

## Table de correspondance (undertone × contraste → saison)

| Undertone | Contraste faible | Contraste moyen | Contraste fort |
|---|---|---|---|
| Chaud | Printemps | Printemps | Automne |
| Froid | Été | Été | Hiver |
| Neutre | Été | Automne | Hiver |

**Logique :** chaud + fort contraste = automne (profondeur + chaleur) ;
chaud + faible/moyen = printemps (légèreté + chaleur) ; froid + fort =
hiver (profondeur + fraîcheur) ; froid + faible/moyen = été (douceur +
fraîcheur). La ligne **"neutre" est la plus incertaine** — en pratique de
color analysis réelle, l'undertone neutre demande des signaux
supplémentaires (couleur des yeux, réaction à l'or/l'argent) pour trancher
correctement ; ici on se base uniquement sur le niveau de contraste, ce
qui est une approximation. C'est la ligne à challenger en priorité.

Le code marque les résultats issus de la ligne "neutre" avec une
confiance plus faible (`confiance: "faible"`) — voir
`backend/app/domain/physique/colorimetrie/rules.py`.

## Ce qui manque encore pour une vraie V1 colorimétrie

- **Validation ou correction de cette table** par Clea (priorité n°1)
- **Palette de couleurs par saison** (codes hex) — non fournie, `palette`
  reste vide dans le résultat pour l'instant. Nécessite soit un contenu de
  Clea (direction design), soit une proposition basée sur les palettes
  standard publiées par saison (à faire seulement sur demande explicite,
  pas improvisé ici).
- **Sous-saisons (12)** — hors scope V1, à réévaluer une fois la V1 en test
