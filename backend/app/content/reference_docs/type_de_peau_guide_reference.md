# Reveal You — Pilier Physique — Type de peau

*(source : `Reveal_You_Pilier_Physique_Type_de_peau.docx`, fourni par Clea — reproduit verbatim)*

✅ **Intégré en V1, en déclaratif uniquement (BROUILLON sur la logique de
mapping)** — voir la note en fin de document.

Le type de peau reflète la production naturelle de sébum et la sensibilité cutanée. Il oriente le choix des textures, des actifs et de la fréquence des soins.

## 1. Normale

### Définition
Peau équilibrée, ni trop grasse ni trop sèche, pores peu visibles, texture lisse et peu d'imperfections.

### Conseils de style
- Une routine simple (nettoyage doux, hydratation légère, protection solaire quotidienne) suffit à maintenir l'équilibre.

## 2. Sèche

### Définition
Production de sébum insuffisante ; la peau peut tirailler, les pores sont peu visibles et la texture est parfois rugueuse ou marquée par des zones de desquamation.

### Conseils de style
- Privilégier des textures riches (crèmes, huiles) et des nettoyants sans sulfates.
- Éviter l'eau très chaude et les exfoliants agressifs.
- Rechercher des ingrédients comme l'acide hyaluronique et les céramides.

## 3. Grasse

### Définition
Production excessive de sébum, brillance visible surtout en zone T (front, nez, menton), pores dilatés, tendance aux imperfections.

### Conseils de style
- Privilégier des textures légères et non comédogènes.
- Nettoyer matin et soir sans sur-nettoyer, ce qui stimule davantage la production de sébum.
- Rechercher des ingrédients matifiants comme la niacinamide ou l'acide salicylique.

## 4. Mixte

### Définition
Zone T (front, nez, menton) plus grasse, joues normales à sèches.

### Conseils de style
- Adapter les soins par zone : produit matifiant sur la zone T, plus hydratant sur les joues.
- Ou utiliser des formules équilibrantes conçues pour les peaux mixtes.

## 5. Sensible

### Définition
Peau réactive, sujette aux rougeurs, tiraillements ou picotements face à certains produits ou facteurs environnementaux.

### Conseils de style
- Privilégier des formules hypoallergéniques et sans parfum.
- Tester tout nouveau produit sur une petite zone avant application complète.
- Limiter le nombre d'actifs utilisés simultanément pour ne pas surcharger la peau.

---

✅ **Note (mise à jour, décision de Clea en session) :** photo jugée trop
peu fiable pour ce cas (Clea : « ce sera un peu compliqué d'analyser le
type de peau avec une photo ») — approche V1 retenue : **3 questions
déclaratives** (ressenti au quotidien, observation visuelle, préoccupation
principale), chacune couvrant un angle déjà présent dans les définitions
ci-dessus. C'est une **4e fonctionnalité du pilier Physique**, comme la
nature des cheveux.

⚠️ **Brouillon non validé : la logique qui combine les 3 réponses pour
déterminer le type.** Le document ci-dessus donne les 5 définitions et
leurs conseils, mais pas de grille officielle "quelle réponse compte pour
quel type" — cette grille a été construite par déduction directe à partir
des définitions (une réponse = un aspect explicitement mentionné dans la
définition du type correspondant, jamais inventé), puis un score simple
(le type le plus souvent pointé par les 3 réponses l'emporte, égalité
tranchée dans l'ordre ressenti → visuel → préoccupation). Voir
`backend/app/domain/physique/peau/type_peau.py` pour le détail exact et
la table de correspondance. **À faire valider par Clea avant mise en
prod**, même logique de prudence que pour la table saison colorielle.
