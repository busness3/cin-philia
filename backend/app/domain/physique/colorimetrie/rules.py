"""Moteur de règles déterministe : undertone + contraste → saison colorielle.

⚠️ Table de correspondance = BROUILLON, pas encore validé par Clea.
Contrairement au reste du produit, aucun document de référence ne donnait
la table exacte (signalé comme point ouvert par Clea elle-même dans
`typologie_pilier_physique.md`). Le détail de la méthode utilisée, ses
limites, et ce qui reste à valider sont documentés dans
`backend/app/content/reference_docs/colorimetrie_saisons_brouillon.md` —
à lire avant de considérer cette table comme définitive.

Portée V1 : 4 saisons de base uniquement (pas de 12 sous-saisons — les
inputs déclaratifs qu'on collecte ne suffisent pas à les distinguer
fiablement). `sous_saison` reste `None` pour l'instant.

100% déterministe (pas d'appel IA) : le résultat doit être reproductible.
"""

from app.schemas.diagnostic import ColorimetrieInput, ColorimetrieResult, NiveauContraste, Undertone

# (undertone, niveau_contraste) -> saison
# Voir colorimetrie_saisons_brouillon.md pour la logique et les réserves,
# notamment sur la ligne "neutre" (la plus incertaine).
SEASON_RULES: dict[tuple[Undertone, NiveauContraste], str] = {
    (Undertone.CHAUD, NiveauContraste.FAIBLE): "Printemps",
    (Undertone.CHAUD, NiveauContraste.MOYEN): "Printemps",
    (Undertone.CHAUD, NiveauContraste.FORT): "Automne",
    (Undertone.FROID, NiveauContraste.FAIBLE): "Été",
    (Undertone.FROID, NiveauContraste.MOYEN): "Été",
    (Undertone.FROID, NiveauContraste.FORT): "Hiver",
    (Undertone.NEUTRE, NiveauContraste.FAIBLE): "Été",
    (Undertone.NEUTRE, NiveauContraste.MOYEN): "Automne",
    (Undertone.NEUTRE, NiveauContraste.FORT): "Hiver",
}

# L'undertone neutre est la ligne la plus incertaine de la table (voir le
# brouillon) — on le reflète dans le niveau de confiance du résultat.
_LOWER_CONFIDENCE_UNDERTONES = {Undertone.NEUTRE}


def determine_season(diagnostic_input: ColorimetrieInput) -> ColorimetrieResult:
    key = (diagnostic_input.undertone, diagnostic_input.niveau_contraste)
    saison = SEASON_RULES[key]  # table complète sur les 9 combinaisons — pas de trou possible

    confiance = "faible" if diagnostic_input.undertone in _LOWER_CONFIDENCE_UNDERTONES else "forte"

    return ColorimetrieResult(saison=saison, sous_saison=None, palette=[], confiance=confiance)
