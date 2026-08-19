"""Nature des cheveux (texture) — lookup déterministe, pas d'IA.

Décision produit (Clea, en session) : contrairement aux catégories
morphologie (silhouette, forme du visage/yeux, sourcils), la nature des
cheveux n'est **pas** classifiée par photo — Clea juge que ce n'est pas
son domaine d'expertise pour le moment et qu'une lecture fiable demande
une vraie connaissance capillaire ; l'analyse photo pourra revenir plus
tard (V2+). En V1 : l'utilisatrice se déclare elle-même (2 choix : type
1-4 puis sous-type A/B/C), on lui restitue directement la description et
les conseils déjà rédigés par Clea pour ce sous-type — pas de génération,
juste un lookup fidèle au document source.

Contenu transcrit verbatim de `backend/app/content/reference_docs/
nature_cheveux_guide_reference.md` (méthode André Walker, fournie par
Clea). Voir docs/CLAUDE.md § Ne jamais halluciner de critères typologiques.
"""

from app.schemas.diagnostic import NatureCheveuxResult, TypeTextureCheveux

_FAMILLE_1 = "Cheveux sans ondulation ni boucle, texture lisse de la racine aux pointes, brillance naturelle marquée."
_FAMILLE_2 = "Cheveux formant un « S » plus ou moins marqué, entre le raide et le bouclé."
_FAMILLE_3 = "Cheveux formant des boucles bien définies en forme de spirale."
_FAMILLE_4 = "Cheveux avec un fort retrait (« shrinkage »), motif très serré, plus fragiles et sujets à la sécheresse."

_EVITER_PRODUITS_LOURDS = "Éviter les produits lourds qui alourdissent et aplatissent la chevelure."
_VOLUME_RACINE = (
    "Utiliser un shampoing volumateur et sécher tête en bas pour donner du volume à la racine."
)

_CHEVEUX_INFO: dict[TypeTextureCheveux, dict[str, str | list[str]]] = {
    TypeTextureCheveux.T1A: {
        "detail": "Très raides et fins, sans volume naturel.",
        "conseils": [_EVITER_PRODUITS_LOURDS, _VOLUME_RACINE],
    },
    TypeTextureCheveux.T1B: {
        "detail": "Raides avec un peu plus de corps et de volume que 1A, texture moyenne.",
        "conseils": [_EVITER_PRODUITS_LOURDS, _VOLUME_RACINE],
    },
    TypeTextureCheveux.T1C: {
        "detail": "Raides mais texture plus épaisse, avec parfois quelques mèches qui ondulent légèrement et un peu de frisottis.",
        "conseils": [
            _EVITER_PRODUITS_LOURDS,
            "Un sérum lissant léger aide à contrôler le frisottis ; éviter le brossage à sec qui crée de l'électricité statique.",
        ],
    },
    TypeTextureCheveux.T2A: {
        "detail": "Ondulations légères et détendues, texture fine à moyenne, volume naturel léger.",
        "conseils": [
            "Appliquer une mousse coiffante légère sur cheveux humides et sécher au diffuseur pour définir sans alourdir.",
        ],
    },
    TypeTextureCheveux.T2B: {
        "detail": "Ondulations plus définies commençant à mi-longueur, légère tendance au frisottis.",
        "conseils": [
            "Utiliser une crème anti-frisottis et la technique du « scrunching » (froisser les longueurs) au séchage.",
        ],
    },
    TypeTextureCheveux.T2C: {
        "detail": "Ondulations bien définies dès la racine, parfois quelques boucles, plus sujettes au volume et au frisottis.",
        "conseils": [
            "Un gel coiffant définit l'ondulation ; la méthode du « plopping » (envelopper les cheveux mouillés dans un t-shirt) limite le frisottis.",
        ],
    },
    TypeTextureCheveux.T3A: {
        "detail": "Boucles larges et souples, bien définies, brillantes.",
        "conseils": [
            "Utiliser une crème coiffante hydratante et démêler les cheveux mouillés avec les doigts ou un peigne à dents larges.",
        ],
    },
    TypeTextureCheveux.T3B: {
        "detail": "Boucles plus serrées, ressort bien marqué, volume important.",
        "conseils": [
            "Adopter une routine « curly girl » (sans sulfates ni silicones) et un gel pour maintenir la définition toute la journée.",
        ],
    },
    TypeTextureCheveux.T3C: {
        "detail": "Boucles très serrées et denses, volume marqué, plus sujettes à la sécheresse.",
        "conseils": [
            "Renforcer l'hydratation avec des masques réguliers et utiliser la technique du « praying hands » pour répartir le produit sans casser les boucles.",
        ],
    },
    TypeTextureCheveux.T4A: {
        "detail": "Boucles en « S » très serrées et définies, ressort visible à l'œil.",
        "conseils": [
            "Hydrater quotidiennement avec la méthode LOC (Liquide-Huile-Crème) et démêler en petites sections.",
        ],
    },
    TypeTextureCheveux.T4B: {
        "detail": "Motif en « Z », boucles moins définies, forme plus angulaire, fort retrait.",
        "conseils": [
            "Utiliser des produits très nourrissants et privilégier des coiffures protectrices à faible manipulation pour limiter la casse.",
        ],
    },
    TypeTextureCheveux.T4C: {
        "detail": "Motif le plus serré, peu ou pas de définition de boucle visible à l'œil nu, retrait maximal, plus fragile.",
        "conseils": [
            "Renforcer l'hydratation et le scellage systématique (LOC/LCO), limiter la chaleur et privilégier des coiffures protectrices avec une manipulation minimale.",
        ],
    },
}

_FAMILLE_DEFINITION: dict[str, str] = {
    "1": _FAMILLE_1,
    "2": _FAMILLE_2,
    "3": _FAMILLE_3,
    "4": _FAMILLE_4,
}


def determine_nature_cheveux(type_texture: TypeTextureCheveux) -> NatureCheveuxResult:
    info = _CHEVEUX_INFO[type_texture]
    famille = type_texture.value[0]  # "1".."4"
    description = f"{_FAMILLE_DEFINITION[famille]} {info['detail']}"
    return NatureCheveuxResult(
        type_texture=type_texture.value,
        description=description,
        conseils_style=list(info["conseils"]),
    )
