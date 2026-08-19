"""Type de peau — lookup + scoring déterministe, pas d'IA, pas de photo.

Décision produit (Clea, en session) : contrairement aux catégories
morphologie, le type de peau n'est **pas** classifié par photo — Clea juge
que ce sera compliqué à analyser fiablement en image. En V1, 3 questions
déclaratives : ressenti au quotidien, observation visuelle, préoccupation
principale — chacune correspondant à un aspect explicitement mentionné
dans les 5 définitions du document de référence.

⚠️ BROUILLON — la grille "quelle réponse compte pour quel type" ci-dessous
est une construction de l'assistant, pas fournie par Clea (le document
donne les 5 définitions et leurs conseils, pas de grille de scoring). Elle
respecte la contrainte "ne jamais halluciner de critères typologiques" au
sens où chaque option d'une question est un extrait direct d'une
définition existante (rien d'inventé sur le contenu), mais la façon de
COMBINER 3 réponses en 1 type est une décision de logique produit qui
reste à valider par Clea — même statut que
`colorimetrie_saisons_brouillon.md`. Voir le détail dans
`backend/app/content/reference_docs/type_de_peau_guide_reference.md`.

Contenu (définitions + conseils) transcrit verbatim du document de
référence. Voir docs/CLAUDE.md § Ne jamais halluciner de critères
typologiques.
"""

from app.schemas.diagnostic import ProblematiquePeau, RessentiPeau, TypePeauResult, VisuelPeau

_TYPES = ["Normale", "Sèche", "Grasse", "Mixte", "Sensible"]

# Chaque réponse "vote" pour le type dont la définition mentionne
# explicitement cet aspect (voir type_de_peau_guide_reference.md).
_RESSENTI_VOTE: dict[RessentiPeau, str] = {
    RessentiPeau.EQUILIBREE: "Normale",
    RessentiPeau.TIRAILLE: "Sèche",
    RessentiPeau.BRILLE: "Grasse",
    RessentiPeau.VARIABLE_SELON_ZONES: "Mixte",
    RessentiPeau.REACTIVE: "Sensible",
}

_VISUEL_VOTE: dict[VisuelPeau, str] = {
    VisuelPeau.PORES_PEU_VISIBLES: "Normale",
    VisuelPeau.ZONES_SECHES: "Sèche",
    VisuelPeau.BRILLANCE_ZONE_T: "Grasse",
    VisuelPeau.ZONE_T_GRASSE_JOUES_SECHES: "Mixte",
    VisuelPeau.ROUGEURS: "Sensible",
}

_PROBLEMATIQUE_VOTE: dict[ProblematiquePeau, str] = {
    ProblematiquePeau.RIEN_DE_PARTICULIER: "Normale",
    ProblematiquePeau.MANQUE_HYDRATATION: "Sèche",
    ProblematiquePeau.IMPERFECTIONS: "Grasse",
    ProblematiquePeau.DOUBLE_BESOIN: "Mixte",
    ProblematiquePeau.REACTIONS_AUX_PRODUITS: "Sensible",
}

_DEFINITIONS: dict[str, str] = {
    "Normale": "Peau équilibrée, ni trop grasse ni trop sèche, pores peu visibles, texture lisse et peu d'imperfections.",
    "Sèche": "Production de sébum insuffisante ; la peau peut tirailler, les pores sont peu visibles et la texture est parfois rugueuse ou marquée par des zones de desquamation.",
    "Grasse": "Production excessive de sébum, brillance visible surtout en zone T (front, nez, menton), pores dilatés, tendance aux imperfections.",
    "Mixte": "Zone T (front, nez, menton) plus grasse, joues normales à sèches.",
    "Sensible": "Peau réactive, sujette aux rougeurs, tiraillements ou picotements face à certains produits ou facteurs environnementaux.",
}

_CONSEILS: dict[str, list[str]] = {
    "Normale": [
        "Une routine simple (nettoyage doux, hydratation légère, protection solaire quotidienne) suffit à maintenir l'équilibre.",
    ],
    "Sèche": [
        "Privilégier des textures riches (crèmes, huiles) et des nettoyants sans sulfates.",
        "Éviter l'eau très chaude et les exfoliants agressifs.",
        "Rechercher des ingrédients comme l'acide hyaluronique et les céramides.",
    ],
    "Grasse": [
        "Privilégier des textures légères et non comédogènes.",
        "Nettoyer matin et soir sans sur-nettoyer, ce qui stimule davantage la production de sébum.",
        "Rechercher des ingrédients matifiants comme la niacinamide ou l'acide salicylique.",
    ],
    "Mixte": [
        "Adapter les soins par zone : produit matifiant sur la zone T, plus hydratant sur les joues.",
        "Ou utiliser des formules équilibrantes conçues pour les peaux mixtes.",
    ],
    "Sensible": [
        "Privilégier des formules hypoallergéniques et sans parfum.",
        "Tester tout nouveau produit sur une petite zone avant application complète.",
        "Limiter le nombre d'actifs utilisés simultanément pour ne pas surcharger la peau.",
    ],
}


def determine_type_peau(
    *,
    ressenti: RessentiPeau,
    visuel: VisuelPeau,
    problematique: ProblematiquePeau,
) -> TypePeauResult:
    # Chaque réponse vote pour un type ; le plus voté l'emporte. Égalité
    # tranchée par priorité de question — ressenti d'abord, puis visuel,
    # puis problématique (ordre des questions elles-mêmes, pas de signal
    # externe pour trancher autrement).
    votes = [_RESSENTI_VOTE[ressenti], _VISUEL_VOTE[visuel], _PROBLEMATIQUE_VOTE[problematique]]
    priorite: dict[str, int] = {}
    for i, t in enumerate(votes):
        priorite.setdefault(t, -i)  # 1re occurrence = priorité la plus haute
    type_peau = max(_TYPES, key=lambda t: (votes.count(t), priorite.get(t, -99)))

    return TypePeauResult(
        type_peau=type_peau,
        description=_DEFINITIONS[type_peau],
        conseils_style=_CONSEILS[type_peau],
    )
