# Contenu de référence produit

Documents de référence de Clea, utilisés comme source de vérité pour les
prompts/règles de classification (`docs/CLAUDE.md` → "Ne jamais halluciner
de critères typologiques"). Verbatim dans `reference_docs/`, chargés à
l'exécution par le code de classification plutôt que dupliqués en dur.

## Statut par catégorie

- [x] **Silhouette (H/A/V/O/X)** — critères complets reçus et intégrés (`silhouettes_guide_reference.md`). Classification fonctionnelle.
- [x] **Colorimétrie (4 saisons)** — fonctionnelle, **2 parcours** : formulaire déclaratif ou photo de visage (Claude vision lit undertone/contraste, voir `photo_classification.py`). Table de correspondance **brouillon non validée** (`colorimetrie_saisons_brouillon.md`) faute de table fournie. À faire relire par Clea en priorité. Contraste (§4) **et** undertone (§8) approfondis : critères complets + conseils de style reçus et intégrés (`contraste_guide_reference.md`, `teint_soustons_guide_reference.md`) — meilleure lecture photo, et `conseils_style` (bijoux/couleurs + association de couleurs/maquillage combinés) maintenant renvoyé dans le résultat.
- [x] **Forme du visage (7 types)** — critères complets reçus et intégrés (`forme_visage_guide_reference.md`) : Ovale, Rond, Carré, Cœur, Allongé, Losange, Triangulaire. Classification fonctionnelle, branchée sur `POST /morphologie/silhouette` (réutilise la photo de face déjà fournie pour la silhouette — pas de photo supplémentaire demandée). **Sort la morphologie du périmètre "silhouette uniquement"** décidé plus bas — mis à jour en conséquence.
- [x] **Forme des yeux (9 types)** — critères complets reçus et intégrés (`forme_yeux_guide_reference.md`) : Amande, Rond, Tombant, Relevé, Monolide, Hooded, Rapprochés, Écartés, Protubérants. Classification fonctionnelle, branchée sur `POST /morphologie/silhouette` (même photo de face que silhouette + forme du visage — pas de photo supplémentaire). ⚠️ Ces 9 types couvrent en réalité 2 axes (forme de l'œil vs espacement) non mutuellement exclusifs — voir note dans `forme_yeux_classification.py` ; gardé en un seul choix pour coller au document source, à revoir avec Clea si besoin de plus de précision.
- [x] **Sourcils (6 types)** — critères complets reçus et intégrés (`sourcils_guide_reference.md`) : Arqués, Droits, Arrondis, Épais, Fins, En pente descendante. Classification fonctionnelle, branchée sur `POST /morphologie/silhouette` (même photo de face que les autres catégories — pas de photo supplémentaire). ⚠️ Le document source formule la catégorie "En pente descendante" dans un vocabulaire correctif ("air fatigué", "corriger") contraire à la charte de ton — reformulation explicitement demandée à Claude dans `sourcils_classification.py`, voir la note dans `sourcils_guide_reference.md`.
- [x] **Nature des cheveux (12 sous-types, André Walker)** — critères complets reçus et intégrés (`nature_cheveux_guide_reference.md`). **3e fonctionnalité du pilier Physique**, distincte de colorimétrie/morphologie. **Déclaratif uniquement, pas de photo/IA** (décision de Clea : la classification par photo demande une expertise capillaire qu'elle n'a pas encore pour la valider — reportée à une itération future). L'utilisatrice choisit famille (1-4) puis sous-type (A/B/C), l'app restitue directement la description + les conseils du document (lookup déterministe, voir `nature_cheveux.py`) — aucune génération IA. Endpoint : `POST /cheveux/nature`.
- [x] **Type de peau (5 types)** — critères complets reçus et intégrés (`type_de_peau_guide_reference.md`) : Normale, Sèche, Grasse, Mixte, Sensible. **4e fonctionnalité du pilier Physique**, déclarative comme les cheveux (Clea : photo jugée trop peu fiable pour cette catégorie). 3 questions (ressenti, observation visuelle, préoccupation principale), chaque option reprenant un aspect déjà présent dans une définition. ⚠️ **BROUILLON non validé : la logique qui combine les 3 réponses en 1 type** (scoring simple, tie-break par ordre de question) — construite par déduction, pas fournie par Clea. Voir la note dans `type_de_peau_guide_reference.md` et le détail dans `type_peau.py`. Endpoint : `POST /peau/type`.

## Décision de périmètre V1 (prise en session, à valider avec Clea)

Le framework typologique complet couvre 9 catégories, mais seules 2
alimentent réellement les 2 fonctionnalités IA déclarées pour la V1
(colorimétrie et morphologie/silhouette). Pour arriver à une V1 complète
et testable maintenant plutôt que bloquée sur des documents manquants,
le périmètre V1 est réduit à ce qui est classifiable dès aujourd'hui :

- ~~**Morphologie V1 = silhouette uniquement.**~~ **Mis à jour** : Clea a
  fourni les critères de la forme du visage, de la forme des yeux et des
  sourcils — la morphologie V1 couvre maintenant silhouette **+** forme
  du visage **+** forme des yeux **+** sourcils (voir statut ci-dessus).
- **Colorimétrie V1 = 4 saisons de base**, pas de 12 sous-saisons (les
  inputs déclaratifs collectés ne suffisent pas à les distinguer
  fiablement).
- ~~**Texture des cheveux : hors scope V1.**~~ **Mis à jour** : Clea a
  fourni les critères et tranché l'approche — 3e fonctionnalité du pilier
  Physique, déclarative (voir statut ci-dessus). Sort donc du hors-scope.
- ~~**Type de peau : hors scope V1.**~~ **Mis à jour** : même chose —
  Clea a tranché pour du déclaratif (photo jugée peu fiable ici) — 4e
  fonctionnalité du pilier Physique (voir statut ci-dessus). Sort du
  hors-scope, mais la logique de scoring reste un brouillon à valider.
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
4. Confirmer la décision de périmètre ci-dessus (silhouette + forme du
   visage + forme des yeux + sourcils dans le scope morphologie ; nature
   des cheveux et type de peau en 3e/4e fonctionnalités déclaratives à
   part).
5. **Forme des yeux — axe forme vs espacement** : à trancher avec Clea si
   elle veut distinguer les deux plutôt qu'un choix unique parmi 9 (voir
   note dans `forme_yeux_classification.py`).
6. **Sourcils — reformulation "En pente descendante"** : à faire confirmer
   par Clea que la reformulation demandée à Claude (sans "air fatigué"
   ni "corriger") rend bien l'esprit voulu, malgré le vocabulaire du
   document source — voir note dans `sourcils_guide_reference.md`.
7. **Type de peau — logique de scoring à valider (priorité).** Les 3
   questions et la grille de correspondance vers les 5 types sont un
   brouillon construit par déduction à partir des définitions du
   document — pas fourni par Clea. À faire relire en priorité, comme la
   table de correspondance saison colorielle. Voir la note dans
   `type_de_peau_guide_reference.md` et `type_peau.py`.
