# Reveal You — Pilier Physique — Définitions et Typologies

*Source : `Reveal_You_Pilier_Physique.pdf` fourni par Clea, copié verbatim ici comme source de vérité pour les prompts de classification.*

## 1. Silhouette (morphologie corporelle)

Basée sur le rapport épaules / taille / hanches.

- **H (rectangle)** — épaules, taille et hanches alignées, peu de creux à la taille
- **A (poire / triangle)** — hanches plus larges que les épaules
- **V (triangle inversé)** — épaules plus larges que les hanches
- **O (ronde / pomme)** — volume concentré au niveau du ventre/taille
- **X (sablier)** — épaules et hanches équilibrées, taille bien marquée

*(Voir `silhouettes_guide_reference.md` pour le détail complet par type, avec critères de repérage.)*

## 2. Forme du visage

⚠️ Noms seulement — critères distinctifs non fournis à date.

- Ovale
- Rond
- Carré
- Cœur
- Allongé (rectangle)
- Losange (diamant)
- Triangulaire (poire)

## 3. Forme des yeux

⚠️ Noms seulement, quelques clarifications partielles — critères de repérage complets non fournis à date.

- Amande
- Rond
- Tombant
- Relevé
- Monolide (sans pli de paupière)
- Hooded (paupière tombante qui cache le pli)
- Rapprochés
- Écartés
- Protubérants (globuleux)

## 4. Contraste

Écart entre l'intensité de la peau, des yeux et des cheveux.

- **Faible (doux)** — éléments proches en intensité, pas de grand écart clair/foncé
- **Moyen** — écart modéré, offre de la flexibilité dans les associations
- **Fort** — grand écart clair/foncé, mieux mis en valeur par des looks contrastés

## 5. Sourcils

⚠️ Noms seulement.

- Arqués
- Droits
- Arrondis
- Épais
- Fins
- En pente descendante

## 6. Type de peau

⚠️ Noms seulement.

- Normale
- Sèche
- Grasse
- Mixte
- Sensible

## 7. Colorimétrie (saison)

⚠️ **Table de correspondance non fournie à date** — voir `docs/CLAUDE.md` et `backend/app/content/README.md`.

- 4 saisons de base : printemps, été, automne, hiver
- Version affinée en 12 sous-saisons (ex. printemps clair, été doux, automne profond, hiver pur) — plus précise mais plus complexe à calculer et à expliquer

## 8. Teint de peau / sous-ton

- **Chaud** → va généralement mieux avec les bijoux/tons dorés
- **Froid** → va généralement mieux avec les bijoux/tons argentés
- **Neutre** → peut porter l'or et l'argent

## 9. Nature des cheveux (texture)

Classification André Walker (méthode publique, pas propriétaire) :

- Type 1 (raides) : 1A, 1B, 1C
- Type 2 (ondulés) : 2A, 2B, 2C
- Type 3 (bouclés) : 3A, 3B, 3C
- Type 4 (crépus) : 4A, 4B, 4C

*Décision à prendre : classification complète (1A-4C) ou version simplifiée en 4 catégories pour le MVP.*

## Points ouverts (statut mis à jour en session de dev)

- ~~Approche technique : API vision existante (prompts) vs modèle custom entraîné~~ → **tranché : API Claude vision + structured outputs**
- Nombre de photos demandées à l'utilisateur (visage seul / visage + corps entier)
- Niveau de détail cheveux pour le MVP (4 types ou 12 sous-types)
- Niveau de détail colorimétrie pour le MVP (4 saisons ou 12 sous-saisons)
