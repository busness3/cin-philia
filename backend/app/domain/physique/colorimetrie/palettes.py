"""Palettes de couleurs révélées par saison colorielle.

⚠️ BROUILLON — voir `backend/app/content/reference_docs/
palettes_saisons_brouillon.md` pour la méthode, les réserves, et ce qui
reste à valider avec Clea. Basé sur les palettes standard publiées de la
méthode "color analysis" 4 saisons (pas inventé de zéro), mais pas encore
relu/validé côté produit.

Clé = valeur `saison` telle que renvoyée par
`app.domain.physique.colorimetrie.rules.SEASON_RULES`.
"""

PALETTES: dict[str, list[str]] = {
    "Printemps": [
        "#FF6F61",  # Corail vif
        "#FFD23F",  # Jaune soleil
        "#8BC34A",  # Vert printemps
        "#4DD0C4",  # Turquoise clair
        "#FFAB76",  # Pêche
        "#5FB0E5",  # Bleu ciel chaud
    ],
    "Été": [
        "#A7C7E7",  # Bleu poudré
        "#B39DDB",  # Lavande
        "#E8A0BF",  # Rose poudré
        "#7C93A8",  # Gris-bleu
        "#C08497",  # Mauve
        "#9CAF88",  # Vert sauge
    ],
    "Automne": [
        "#C1652F",  # Terracotta
        "#D4A017",  # Moutarde
        "#6B7A3A",  # Vert olive
        "#6F4E37",  # Brun chocolat
        "#BF5B23",  # Orange brûlé
        "#7B241C",  # Bordeaux
    ],
    "Hiver": [
        "#C8102E",  # Rouge vrai
        "#002F87",  # Bleu roi
        "#00693E",  # Émeraude
        "#C6007E",  # Fuchsia
        "#1A1A1A",  # Noir
        "#A9D6E5",  # Bleu glacier
    ],
}
