"""Conseils de style par undertone — transcrits verbatim des "Conseils de
style" de `backend/app/content/reference_docs/teint_soustons_guide_reference.md`
(fourni par Clea).

Même principe que `contraste_conseils.py` : lookup déterministe sur 3
valeurs fixes plutôt que parsing du markdown à l'exécution.
"""

from app.schemas.diagnostic import Undertone

UNDERTONE_CONSEILS: dict[Undertone, list[str]] = {
    Undertone.CHAUD: [
        "Les bijoux et métaux dorés ou cuivrés mettent le teint en valeur.",
        "Les couleurs chaudes (camel, kaki, corail, ivoire) sont particulièrement flatteuses.",
        "En maquillage, privilégier des fonds de teint à base jaune ou dorée.",
    ],
    Undertone.FROID: [
        "Les bijoux et métaux argentés ou platine mettent le teint en valeur.",
        "Les couleurs froides (bleu marine, gris, fuchsia, blanc pur) sont flatteuses.",
        "En maquillage, privilégier un fond de teint à base rosée ou neutre-froide.",
    ],
    Undertone.NEUTRE: [
        "Peut porter à la fois l'or et l'argent sans contrainte.",
        "Grande liberté dans le choix des couleurs — sert souvent de « joker » dans une palette.",
    ],
}
