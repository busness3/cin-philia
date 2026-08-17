"""Palettes de couleurs révélées par saison colorielle.

⚠️ BROUILLON — voir `backend/app/content/reference_docs/
colorimetrie_palettes_12_saisons.md` pour la méthode, les images de
référence utilisées, et ce qui reste à valider avec Clea. Codes hex
estimés visuellement à partir des images fournies + la méthode standard
12 saisons publiée dans le secteur (pas inventés de zéro), mais pas
encore relus/validés côté produit.

`PALETTES` (4 saisons de base) est ce qu'utilise la V1 actuelle — chaque
entrée correspond à la sous-saison "pure" de `SUBSEASON_PALETTES`
(Warm Spring, Cool Summer, Warm Autumn, Cool Winter), qui est la seule
sous-saison directement déductible de nos 2 inputs actuels (undertone +
contraste). Voir la doc de référence pour pourquoi les 12 sous-saisons ne
sont pas encore classifiables (il manque un 3e axe diagnostique : éclat/
intensité, pas encore collecté).
"""

SUBSEASON_PALETTES: dict[str, list[str]] = {
    # Printemps (chaud, clair, éclatant)
    "Light Spring": ["#F6D9B0", "#F4B896", "#A9D8B8", "#C9E4A8", "#A8D4D8", "#B8CDE8"],
    "Warm Spring": ["#E8895C", "#E0A030", "#C8AA3C", "#4E9E88", "#E86868", "#70A8A0"],
    "Bright Spring": ["#FF6B4A", "#FFC72C", "#2FA88C", "#3D7DD8", "#E8447A", "#7ED321"],
    # Été (froid, clair, doux)
    "Light Summer": ["#F0D9DC", "#E5CFE0", "#C8D8C0", "#B8CEDE", "#C7C4E0", "#A8B8C8"],
    "Cool Summer": ["#9A4E6E", "#B85A8A", "#E0357A", "#4472A8", "#2C5C9E", "#5C90C8"],
    "Soft Summer": ["#B08890", "#9C8080", "#90A090", "#6E9E96", "#4E8C88", "#78889C"],
    # Automne (chaud, profond, mat)
    "Soft Autumn": ["#B89878", "#A8A078", "#8CA084", "#6E9088", "#A87868", "#8C7868"],
    "Warm Autumn": ["#C1652F", "#D4A017", "#6B7A3A", "#B85C20", "#8C5A2C", "#A03828"],
    "Deep Autumn": ["#6F2C1C", "#7A3A10", "#2C4A2C", "#1C3C4A", "#4A1C3C", "#2C2418"],
    # Hiver (froid, profond, éclatant)
    "Cool Winter": ["#7B2FA0", "#C8106E", "#1C4C9C", "#14807A", "#4C4C9C", "#E4E8EC"],
    "Deep Winter": ["#4A0E28", "#2C0A3C", "#0C2C4A", "#0C3C2C", "#1A1A1A", "#3C0A1A"],
    "Bright Winter": ["#E0146E", "#C8102E", "#0028A0", "#7B10A0", "#00A088", "#1A1A1A"],
}

# Saison de base -> sous-saison "pure" correspondante (température seule,
# sans les axes clarté/éclat qu'on ne collecte pas encore).
_PURE_SUBSEASON_BY_SEASON = {
    "Printemps": "Warm Spring",
    "Été": "Cool Summer",
    "Automne": "Warm Autumn",
    "Hiver": "Cool Winter",
}

PALETTES: dict[str, list[str]] = {
    season: SUBSEASON_PALETTES[subseason] for season, subseason in _PURE_SUBSEASON_BY_SEASON.items()
}
