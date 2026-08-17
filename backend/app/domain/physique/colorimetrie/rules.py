"""Moteur de règles déterministe : undertone + contraste + cheveux → saison.

Volontairement 100% déterministe, pas d'appel IA — le résultat doit être
reproductible et vérifiable, et la classification "saison colorielle" ne
demande pas de jugement visuel, juste une table de correspondance.

⚠️ TODO — bloqué en attente du document de référence de Clea :
La table de correspondance exacte (quelle combinaison undertone/contraste/
cheveux donne quelle saison + sous-saison) n'est pas encore définie ici.
Ne PAS inventer ces seuils — le principe du projet est explicite là-dessus
(voir docs/CLAUDE.md § Ne jamais halluciner de critères typologiques).
Compléter `SEASON_RULES` avec le contenu du document de Clea avant de
sortir cette fonction du statut prototype.
"""

from app.schemas.diagnostic import ColorimetrieInput, ColorimetrieResult, NiveauContraste, Undertone

# Table de correspondance (undertone, niveau_contraste) -> (saison, sous_saison).
# À compléter avec les vraies règles du document de référence.
SEASON_RULES: dict[tuple[Undertone, NiveauContraste], tuple[str, str]] = {}


def determine_season(diagnostic_input: ColorimetrieInput) -> ColorimetrieResult:
    key = (diagnostic_input.undertone, diagnostic_input.niveau_contraste)

    if key not in SEASON_RULES:
        raise NotImplementedError(
            "Table de correspondance saison colorielle non encore définie "
            "pour cette combinaison. Voir TODO en tête de fichier — il "
            "manque le document de référence de Clea pour compléter "
            "SEASON_RULES."
        )

    saison, sous_saison = SEASON_RULES[key]
    return ColorimetrieResult(saison=saison, sous_saison=sous_saison, palette=[])
