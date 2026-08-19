"""Conseils de style par niveau de contraste — transcrits verbatim des
"Conseils de style" de `backend/app/content/reference_docs/
contraste_guide_reference.md` (fourni par Clea).

Table statique plutôt que parsing du markdown à l'exécution : contrairement
aux classifications Claude vision (qui chargent le document en entier, le
contenu variant selon l'image), ici c'est un lookup déterministe sur 3
valeurs fixes — mêmes garanties de fidélité au document source, plus
simple et plus robuste qu'un parsing de sections markdown par titre.
"""

from app.schemas.diagnostic import NiveauContraste

CONTRASTE_CONSEILS: dict[NiveauContraste, list[str]] = {
    NiveauContraste.FAIBLE: [
        "Des looks tout en douceur, avec des teintes proches les unes des autres (camaïeu, dégradés de couleurs voisines).",
        "Les contrastes très marqués (ex. noir et blanc purs) peuvent écraser le visage — à éviter.",
        "En maquillage, estomper les transitions plutôt que de marquer des lignes nettes.",
    ],
    NiveauContraste.MOYEN: [
        "La plupart des associations de couleurs fonctionnent naturellement.",
        "De la flexibilité pour jouer aussi bien sur des looks doux que légèrement contrastés selon l'occasion.",
    ],
    NiveauContraste.FORT: [
        "Des looks avec un vrai contraste (noir et blanc, couleur vive sur base neutre) qui répondent au contraste naturel du visage.",
        "Les looks trop doux ou ton sur ton peuvent paraître fades sur ce profil.",
        "En maquillage, des lignes nettes (eyeliner graphique, lèvres marquées) sont particulièrement flatteuses.",
    ],
}
