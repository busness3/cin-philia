# Reveal You (alias : Reveal Glow) — Spécifications produit

## 🎯 Vision & Philosophie

**Reveal You** est une application de développement personnel dont la promesse centrale est de **révéler qui la personne est déjà**, plutôt que de la pousser à se transformer ou à s'améliorer.

Cette philosophie est **structurante**, pas juste un argument marketing : elle conditionne le ton, les textes, le design et le cadrage de chaque fonctionnalité.

### Règles de ton non-négociables
- ❌ Jamais d'imagerie "avant/après"
- ❌ Jamais de vocabulaire correctif ("corriger", "améliorer", "cacher un défaut")
- ❌ Jamais de jugement implicite sur un type morphologique/coloriel par rapport à un autre
- ✅ Ton chaleureux, bienveillant, non-jugeant — comme un coach qui accompagne, pas un juge qui évalue
- ✅ Vocabulaire descriptif : on "révèle", on "met en lumière", on "explore" — jamais on ne "corrige"

## 🏗️ Structure produit : les 4 piliers

L'app est conçue autour de 4 piliers de développement personnel :
1. **Physique** ← **SCOPE DE LA V1**
2. Mental
3. Organisation
4. Finances / Carrière

**Important pour le développement : la V1 se concentre exclusivement sur le pilier Physique.** L'architecture doit néanmoins être pensée pour accueillir les 3 autres piliers plus tard (navigation, modèle de données, structure de l'app extensible).

## 📱 V1 — Pilier Physique : 2 fonctionnalités IA

⚠️ **Décision de périmètre (prise en session, à valider avec Clea)** — pour
livrer une V1 complète et testable plutôt que bloquée sur des documents
manquants, le périmètre a été resserré à ce qui est classifiable dès
aujourd'hui. Détail complet et raisons dans
`backend/app/content/README.md` § Décision de périmètre V1. Résumé :
- Morphologie V1 = **silhouette + forme du visage + forme des yeux +
  sourcils** (mise à jour : Clea a fourni les critères des 4, qui sortent
  donc du différé)
- Colorimétrie V1 = **4 saisons de base** (pas de 12 sous-saisons)
- Type de peau / texture cheveux : hors scope V1
- Photos silhouette : **2 obligatoires** (face + profil — comble la limite de précision ~50% d'une seule photo), la vue de face sert aussi à la forme du visage, la forme des yeux et les sourcils (pas de photo supplémentaire). Photos colorimétrie : **2 optionnelles** (alternative au formulaire, pas obligatoire).

### 1. Diagnostic de colorimétrie
Détermine la saison colorielle de l'utilisateur·rice (système 4 saisons — 12 sous-saisons différées, voir décision de périmètre ci-dessus), via **2 parcours au choix** :
- **Formulaire déclaratif** : undertone, niveau de contraste (faible/moyen/fort), couleur des cheveux
- **2 photos de visage** : Claude vision lit l'undertone et le contraste sur chaque photo et croise les 2 lectures (mêmes définitions, même moteur de règles ensuite) — plus précis pour qui ne sait pas s'auto-évaluer ; confiance dégradée explicitement si les 2 lectures divergent ou si l'éclairage semble trompeur, avec une consigne de capture (lumière naturelle, sans maquillage/filtre, idéalement 2 moments différents). Voir `backend/app/domain/physique/colorimetrie/photo_classification.py`.

→ Résultat : palette de couleurs qui "révèlent" la personne (jamais "qui l'avantagent" ou "qui la flattent" — reformuler en langage non-correctif), accompagnée de **2-3 conseils de style liés au niveau de contraste déclaré** (association de couleurs, maquillage) — issus de `backend/app/content/reference_docs/contraste_guide_reference.md` (fourni par Clea), voir `contraste_conseils.py`. **La table de correspondance undertone+contraste→saison est un brouillon non validé** (voir `backend/app/content/reference_docs/colorimetrie_saisons_brouillon.md`) — aucune table n'ayant été fournie, un brouillon basé sur la méthode standard de color analysis a été posé pour débloquer la V1, à faire relire par Clea.

### 2. Analyse morphologique (silhouette + forme du visage + forme des yeux + sourcils) + recommandations
En V1, couvre la silhouette, la forme du visage, la forme des yeux **et** les sourcils (mise à jour : critères des 4 reçus, plus différés — voir décision de périmètre), avec des recommandations vestimentaires/lunettes/coiffure/bijoux/maquillage cohérentes avec les types identifiés.

**Contrainte technique connue :** la classification de silhouette à partir d'une seule image a une précision d'environ 50% même avec des modèles robustes. **Approche V1 implémentée : hybride + 2 photos** — mesures déclarées par l'utilisateur·rice + analyse visuelle sur une vue de face ET une vue de profil (plutôt qu'une seule image), pour couvrir les volumes que la vue de face seule ne montre pas.

**Forme du visage, forme des yeux et sourcils :** classification à partir de la même vue de face (une seule photo suffit, se lisent entièrement de face) — voir `backend/app/domain/physique/morphologie/forme_visage_classification.py`, `forme_yeux_classification.py` et `sourcils_classification.py`. 7 catégories de forme de visage (Ovale, Rond, Carré, Cœur, Allongé, Losange, Triangulaire), 9 de forme des yeux (Amande, Rond, Tombant, Relevé, Monolide, Hooded, Rapprochés, Écartés, Protubérants — ⚠️ ces 9 couvrent 2 axes différents, forme et espacement, non tranchés séparément, voir note dans le fichier) et 6 de sourcils (Arqués, Droits, Arrondis, Épais, Fins, En pente descendante — ⚠️ cette dernière catégorie est reformulée par Claude pour retirer le vocabulaire correctif du document source, voir note dans `sourcils_guide_reference.md`). Résultats combinés avec la silhouette en un seul appel (`POST /morphologie/silhouette`), chacun non bloquant si sa classification échoue seule.

## 🧬 Framework typologique complet (9 catégories)

Ordre diagnostique défini :

1. **Silhouette** — typologie H / A / V / O / X
2. **Forme du visage** — 7 types
3. **Forme des yeux** — 9 types
4. **Niveau de contraste** — (alimente la colorimétrie)
5. **Sourcils**
6. **Type de peau**
7. **Saison colorielle** — système 4 saisons + 12 sous-saisons (résultat dérivé des catégories 4, 8, et couleur des cheveux)
8. **Ton de peau / undertone** — (alimente la colorimétrie)
9. **Texture des cheveux** — méthode André Walker, types 1A à 4C

**Dépendances importantes pour la logique métier :**
Undertone + Niveau de contraste + Couleur des cheveux → déterminent ensemble le résultat de Saison colorielle. Ces 3 inputs doivent être capturés avant de pouvoir calculer la saison.

**Documents de référence (reçus et intégrés dans `backend/app/content/reference_docs/`) :**
- ✅ `typologie_pilier_physique.md` — définitions et typologies des 9 catégories (source : `Reveal_You_Pilier_Physique.pdf`)
- ✅ `silhouettes_guide_reference.md` — critères complets de repérage par type de silhouette (source : `Morphologies_Reveal_You.docx`) — **classification silhouette fonctionnelle en V1**
- ✅ `forme_visage_guide_reference.md` — définitions + conseils de style pour les 7 formes de visage (source : `Reveal_You_Pilier_Physique_Forme_du_visage.docx`) — **classification forme du visage fonctionnelle en V1**
- ✅ `forme_yeux_guide_reference.md` — définitions + conseils de maquillage pour les 9 formes des yeux (source : `Reveal_You_Pilier_Physique_Forme_des_yeux.docx`) — **classification forme des yeux fonctionnelle en V1**
- ✅ `contraste_guide_reference.md` — définitions détaillées + conseils de style pour les 3 niveaux de contraste (source : `Reveal_You_Pilier_Physique_Contraste.docx`) — **approfondit le §4 de `typologie_pilier_physique.md`**, utilisé pour la lecture photo et pour les conseils de style du résultat colorimétrie
- ✅ `sourcils_guide_reference.md` — définitions + conseils d'entretien/maquillage pour les 6 formes de sourcils (source : `Reveal_You_Pilier_Physique_Sourcils.docx`) — **classification sourcils fonctionnelle en V1**

Ces documents sont rédigés dans un langage descriptif et non-correctif, cohérent avec le positionnement de la marque. **Si le détail précis d'une catégorie manque pour implémenter la logique de classification, demander à l'utilisatrice de fournir le contenu du document correspondant plutôt que d'inventer des critères.**

⚠️ **Non résolu à date :**
- Table de correspondance saison colorielle (undertone + contraste + cheveux → saison/sous-saison) — le framework est reçu, pas la table elle-même.

Voir `backend/app/content/README.md` pour le détail à jour de ce qui bloque quoi.

## 🤖 Approche technique pour la classification IA

### Constat général
Il n'existe **pas de dataset unique** couvrant toutes les typologies définies. Une pipeline d'annotation custom sera probablement nécessaire pour plusieurs catégories.

### Décision (mise à jour en session) : classification via Claude API plutôt que pipeline ML maison
Plutôt que d'entraîner des classifieurs custom (bloqué par l'absence de dataset couvrant nos typologies), la V1 utilise l'API Claude (vision multimodale + structured outputs) contrainte aux catégories exactes définies dans les documents de référence de Clea. Ceci évite le chantier d'annotation de dataset pour la V1. L'entraînement d'un modèle custom (via des datasets publics remappés à notre taxonomie, ou nos propres données collectées avec consentement) reste une optimisation V2+ envisageable si le volume/coût le justifie — voir `backend/app/domain/physique/morphologie/README.md`.

### Datasets identifiés (pour référence future, V2+ uniquement)
- Style4BodyShape, CAESAR — silhouette
- CelebA, FFHQ — visages non-annotés (base pour landmarks)
- Roboflow Eye Shape dataset — yeux (couverture partielle)
- Kaggle Face Shape Dataset — visage
- MPIIGaze — regard (à évaluer pertinence)

## 💰 Modèle économique

**Freemium, prix bas** (~2–5€/mois).

**Différenciateur clé — non négociable produit :** le tier gratuit doit être **réellement utile**, pas juste un teaser. Concrètement : **un diagnostic complet gratuit** (pas une version tronquée).

C'est une décision de valeurs autant qu'une décision de croissance — à respecter dans toute logique de paywall/limitation qu'on implémente.

### Concurrents étudiés (positionnement différenciant)
- Glam Up
- Beautify / Glow Up
- LookSky

Ces apps ont des tiers gratuits qui fonctionnent surtout comme des teasers → c'est précisément ce que Reveal You ne fait pas.

## 🎨 Direction visuelle / design

- Palettes de couleurs chaudes et lumineuses
- Typographie arrondie, humaniste
- Formes organiques, douces
- Ambiance générale : **coach bienveillant qui prend soin**, PAS une app beauté générique ou wellness générique
- Éviter absolument les codes visuels "avant/après" ou les esthétiques cliniques/correctives

## 🔒 Principes de confidentialité des données (ajouté en session)

- **Minimisation stricte** : les photos ne sont **jamais persistées**. Traitement en mémoire uniquement, le temps de l'appel à l'API de classification, puis suppression immédiate.
- **Seuls les résultats dérivés** (saison colorielle, type de silhouette, etc. — jamais l'image brute) sont stockés en base.
- **Finalité limitée** : les données ne servent qu'à fournir le diagnostic demandé — pas de réutilisation pour entraînement, marketing ou revente à des tiers.
- **Sous-traitant IA déclaré** : l'API Claude (Anthropic) traite les photos pour la classification (sous-traitant RGPD) — à documenter explicitement dans la politique de confidentialité. Vérifier les conditions de rétention/usage actuelles de l'API avant rédaction finale de la politique.
- Si un usage futur des données pour entraîner un modèle custom est envisagé (V2+), il nécessitera un **opt-in explicite et distinct**, jamais implicite.

## 🗺️ Roadmap au-delà de la V1 (pour information — pas à développer maintenant)

- Widget quotidien "mindset" avec phrases courtes originales (nécessite développement natif)
- Quiz de chronotype
- Guidance nutrition/sport basée sur le cycle menstruel (cadrée comme exploratoire, jamais comme un avis médical)
- Piliers Mental, Organisation, Finances/Carrière
- Évaluation d'un modèle de classification custom entraîné (si le volume utilisateur justifie le coût vs l'API Claude)

## 👥 Équipe & fonctionnement

- Clea : produit, contenu, direction design
- Un développeur ami spécialisé IA/app : implémentation technique
- Travail en français sur toute la documentation et le contenu produit

## ⚙️ Principes de développement à respecter

1. **Discipline MVP** : construire de façon incrémentale, un V1 focalisé plutôt que tout attaquer en même temps. Ne pas sur-engineerer les 3 autres piliers avant que le pilier Physique fonctionne.
2. **Ne jamais halluciner de critères typologiques** : si un détail de classification manque (ex. traits du visage par forme), le signaler et demander le contenu de référence plutôt que d'inventer.
3. **Cohérence de ton systématique** : tout texte généré par l'app (résultats de diagnostic, micro-copy, notifications) doit respecter la philosophie "reveal, not transform".
4. **Architecture extensible** : penser le modèle de données et la navigation pour accueillir les 3 piliers futurs, même si seul Physique est implémenté en V1.
5. **Privacy by design** : aucune photo utilisateur n'est jamais persistée sur disque, en base, ou dans les logs — traitement en mémoire uniquement.

---

*Ce fichier sert de contexte produit pour le développement avec Claude Code.*
