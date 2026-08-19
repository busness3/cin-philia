# Contenu de référence produit

Documents de référence de Clea, utilisés comme source de vérité pour les
prompts/règles de classification (`docs/CLAUDE.md` → "Ne jamais halluciner
de critères typologiques"). Verbatim dans `reference_docs/`, chargés à
l'exécution par le code de classification plutôt que dupliqués en dur.

## Statut par catégorie

- [x] **Silhouette (H/A/V/O/X)** — critères complets reçus et intégrés (`silhouettes_guide_reference.md`). Classification fonctionnelle.
- [x] **Colorimétrie (4 saisons)** — fonctionnelle, **2 parcours** : formulaire déclaratif ou photo de visage (Claude vision lit undertone/contraste, voir `photo_classification.py`). Table de correspondance **brouillon non validée** (`colorimetrie_saisons_brouillon.md`) faute de table fournie. À faire relire par Clea en priorité.
- [x] **Forme du visage (7 types)** — critères complets reçus et intégrés (`forme_visage_guide_reference.md`) : Ovale, Rond, Carré, Cœur, Allongé, Losange, Triangulaire. Classification fonctionnelle, branchée sur `POST /morphologie/silhouette` (réutilise la photo de face déjà fournie pour la silhouette — pas de photo supplémentaire demandée). **Sort la morphologie du périmètre "silhouette uniquement"** décidé plus bas — mis à jour en conséquence.
- [ ] **Forme des yeux (9+ types)** — hors scope V1. Noms + quelques clarifications partielles reçus, critères de repérage complets manquants.
- [ ] **Sourcils, type de peau, texture des cheveux** — hors scope V1 (voir décision de périmètre ci-dessous).

## Décision de périmètre V1 (prise en session, à valider avec Clea)

Le framework typologique complet couvre 9 catégories, mais seules 2
alimentent réellement les 2 fonctionnalités IA déclarées pour la V1
(colorimétrie et morphologie/silhouette). Pour arriver à une V1 complète
et testable maintenant plutôt que bloquée sur des documents manquants,
le périmètre V1 est réduit à ce qui est classifiable dès aujourd'hui :

- ~~**Morphologie V1 = silhouette uniquement.**~~ **Mis à jour** : Clea a
  fourni les critères de la forme du visage — la morphologie V1 couvre
  maintenant silhouette **et** forme du visage (voir statut ci-dessus).
- **Colorimétrie V1 = 4 saisons de base**, pas de 12 sous-saisons (les
  inputs déclaratifs collectés ne suffisent pas à les distinguer
  fiablement).
- **Yeux, sourcils, type de peau, texture des cheveux (André Walker) : hors
  scope V1.** Aucun des 2 features V1 déclarées n'en a besoin — ce sont
  des catégories du framework typologique complet, probablement destinées
  à des fonctionnalités futures (maquillage, soins...) non encore cadrées.
- **Capture photo :** silhouette = **2 photos obligatoires** (face + profil
  — la vue de profil comble la limite de précision (~50%) d'une seule
  photo, déjà signalée dans le doc produit). Colorimétrie = **2 photos
  visage optionnelles** (alternative au formulaire ; 2 photos pour croiser
  la lecture undertone/contraste et fiabiliser la confiance, voir
  `photo_classification.py`). L'utilisatrice choisit formulaire ou photo
  pour la colorimétrie ; jamais l'un ou l'autre imposé. Total possible en
  V1 : jusqu'à 4 photos (2 silhouette + 2 colorimétrie), aucune jamais
  persistée.

Rien n'est perdu : tout le contenu reçu est conservé dans
`reference_docs/` pour reprendre ces catégories dès que le produit en a
besoin.

## Ce qui reste à valider avec Clea (priorité)

1. **Table de correspondance saison colorielle** — brouillon en place, basé
   sur la méthode standard de color analysis, PAS validé (voir
   `colorimetrie_saisons_brouillon.md`). La ligne "undertone neutre" est la
   plus incertaine.
2. ✅ **Palette de couleurs par saison** (codes hex) — **validée par Clea
   pour une V1** (« Pour une première version c'est bien »). Basée sur les
   8 chartes de référence fournies par Clea, échantillonnée **par pixel**
   (pas à l'œil) sur une seule d'entre elles (`colorimetrie_palettes_12_saisons.md`
   / `palettes.py`). Reste ouvert pour plus tard, si besoin : les chartes
   colorislab proposent un rendu plus proche de l'identité de marque mais
   distinguent "True Autumn" / "Warm Autumn" comme 2 palettes différentes
   (notre modèle n'en a qu'une) — non tranché, pas bloquant pour la V1.
3. **Nouvelle question à valider pour passer aux 12 sous-saisons** :
   il manque un 3e axe diagnostique (éclat/intensité des couleurs) — les
   12 palettes sont prêtes (`SUBSEASON_PALETTES`) mais pas branchées tant
   que cette question n'est pas validée. Proposition de wording dans
   `colorimetrie_palettes_12_saisons.md`.
4. Confirmer la décision de périmètre ci-dessus (yeux/sourcils/peau/cheveux
   toujours hors scope — silhouette + forme du visage sont maintenant
   toutes les deux dans le scope morphologie).
5. Document forme des yeux — à fournir quand cette catégorie repasse dans le scope.
