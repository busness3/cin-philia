# Contenu de référence produit

Documents de référence de Clea, utilisés comme source de vérité pour les
prompts/règles de classification (`docs/CLAUDE.md` → "Ne jamais halluciner
de critères typologiques"). Verbatim dans `reference_docs/`, chargés à
l'exécution par le code de classification plutôt que dupliqués en dur.

## Statut par catégorie

- [x] **Silhouette (H/A/V/O/X)** — critères complets reçus et intégrés (`silhouettes_guide_reference.md`). Classification fonctionnelle.
- [x] **Colorimétrie (4 saisons)** — fonctionnelle, mais via une table **brouillon non validée** (`colorimetrie_saisons_brouillon.md`) faute de table de correspondance fournie. À faire relire par Clea en priorité.
- [ ] **Forme du visage (7 types)** — hors scope V1 (voir décision de périmètre ci-dessous). Noms reçus, critères distinctifs toujours non fournis.
- [ ] **Forme des yeux (9+ types)** — hors scope V1. Noms + quelques clarifications partielles reçus, critères de repérage complets manquants.
- [ ] **Sourcils, type de peau, texture des cheveux** — hors scope V1 (voir décision de périmètre ci-dessous).

## Décision de périmètre V1 (prise en session, à valider avec Clea)

Le framework typologique complet couvre 9 catégories, mais seules 2
alimentent réellement les 2 fonctionnalités IA déclarées pour la V1
(colorimétrie et morphologie/silhouette). Pour arriver à une V1 complète
et testable maintenant plutôt que bloquée sur des documents manquants,
le périmètre V1 est réduit à ce qui est classifiable dès aujourd'hui :

- **Morphologie V1 = silhouette uniquement.** La forme du visage est
  différée à une itération suivante (ses critères ne sont de toute façon
  pas encore définis, y compris côté document source de Clea).
- **Colorimétrie V1 = 4 saisons de base**, pas de 12 sous-saisons (les
  inputs déclaratifs collectés ne suffisent pas à les distinguer
  fiablement).
- **Yeux, sourcils, type de peau, texture des cheveux (André Walker) : hors
  scope V1.** Aucun des 2 features V1 déclarées n'en a besoin — ce sont
  des catégories du framework typologique complet, probablement destinées
  à des fonctionnalités futures (maquillage, soins...) non encore cadrées.
- **Conséquence sur la capture photo :** 1 seule photo nécessaire en V1
  (corps entier, pour la silhouette) — pas de photo visage tant que la
  forme du visage n'est pas implémentée.

Rien n'est perdu : tout le contenu reçu est conservé dans
`reference_docs/` pour reprendre ces catégories dès que le produit en a
besoin.

## Ce qui reste à valider avec Clea (priorité)

1. **Table de correspondance saison colorielle** — brouillon en place, basé
   sur la méthode standard de color analysis, PAS validé (voir
   `colorimetrie_saisons_brouillon.md`). La ligne "undertone neutre" est la
   plus incertaine.
2. **Palette de couleurs par saison** (codes hex) — brouillon en place,
   basé sur les 2 images de référence fournies par Clea + la méthode
   standard 12 saisons (`colorimetrie_palettes_12_saisons.md` /
   `palettes.py`), PAS validé (estimation visuelle, pas une extraction
   précise). À comparer aux vraies teintes et à la direction visuelle de
   marque avant mise en prod.
3. **Nouvelle question à valider pour passer aux 12 sous-saisons** :
   il manque un 3e axe diagnostique (éclat/intensité des couleurs) — les
   12 palettes sont prêtes (`SUBSEASON_PALETTES`) mais pas branchées tant
   que cette question n'est pas validée. Proposition de wording dans
   `colorimetrie_palettes_12_saisons.md`.
4. Confirmer la décision de périmètre ci-dessus (silhouette seule pour la
   morphologie V1, yeux/sourcils/peau/cheveux hors scope).
5. Documents formes de visage / formes des yeux — à fournir quand cette
   catégorie repasse dans le scope.
