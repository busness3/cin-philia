# Colorimétrie — palettes de couleurs par saison (BROUILLON — à valider par Clea)

⚠️ **Statut : brouillon, pas une décision produit validée.** Comme pour la
table de correspondance saison (`colorimetrie_saisons_brouillon.md`),
aucune palette n'a été fournie par Clea. Ce document s'appuie sur les
palettes standard publiées dans la méthode de "color analysis" 4 saisons
— un système utilisé partout dans le secteur mode/beauté, pas inventé de
zéro. **À relire et ajuster avant mise en prod**, en particulier pour
vérifier la cohérence avec la direction visuelle de la marque ("palettes
chaudes et lumineuses", voir `docs/CLAUDE.md` § Direction visuelle) — les
palettes Été et Hiver ci-dessous sont volontairement plus froides/sourdes
puisque c'est ce que ces saisons révèlent chez la personne, même si ça
tranche avec l'ambiance générale de l'app.

## Principe

Chaque saison a des couleurs qui partagent sa "signature" (chaleur +
profondeur/clarté) — cohérent avec la logique de la table de
correspondance :
- **Printemps** (chaud, clair) → couleurs chaudes, claires, vives
- **Été** (froid, clair/moyen) → couleurs froides, douces, poudrées
- **Automne** (chaud, foncé) → couleurs chaudes, profondes, terreuses
- **Hiver** (froid, foncé) → couleurs froides, profondes, franches

## Palettes (6 couleurs par saison)

### Printemps
| Couleur | Hex |
|---|---|
| Corail vif | `#FF6F61` |
| Jaune soleil | `#FFD23F` |
| Vert printemps | `#8BC34A` |
| Turquoise clair | `#4DD0C4` |
| Pêche | `#FFAB76` |
| Bleu ciel chaud | `#5FB0E5` |

### Été
| Couleur | Hex |
|---|---|
| Bleu poudré | `#A7C7E7` |
| Lavande | `#B39DDB` |
| Rose poudré | `#E8A0BF` |
| Gris-bleu | `#7C93A8` |
| Mauve | `#C08497` |
| Vert sauge | `#9CAF88` |

### Automne
| Couleur | Hex |
|---|---|
| Terracotta | `#C1652F` |
| Moutarde | `#D4A017` |
| Vert olive | `#6B7A3A` |
| Brun chocolat | `#6F4E37` |
| Orange brûlé | `#BF5B23` |
| Bordeaux | `#7B241C` |

### Hiver
| Couleur | Hex |
|---|---|
| Rouge vrai | `#C8102E` |
| Bleu roi | `#002F87` |
| Émeraude | `#00693E` |
| Fuchsia | `#C6007E` |
| Noir | `#1A1A1A` |
| Bleu glacier | `#A9D6E5` |

## Source de vérité pour le code

`backend/app/domain/physique/colorimetrie/palettes.py` — même table,
format Python. Si Clea fournit des palettes définitives, mettre à jour
les deux fichiers ensemble (ou supprimer ce doc et ne garder que le code
une fois validé).

## Ce qui manque encore

- Validation ou remplacement complet par Clea (direction design)
- Cohérence avec la palette de marque générale de l'app (actuellement
  définie séparément dans `mobile/src/theme/tokens.ts` — pas la même
  chose que les palettes "révélées" par saison, à ne pas confondre)
- Les 12 sous-saisons n'ont pas de palette dédiée — hors scope V1
