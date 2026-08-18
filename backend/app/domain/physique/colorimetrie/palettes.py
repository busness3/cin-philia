"""Palettes de couleurs révélées par saison colorielle.

⚠️ BROUILLON — voir `backend/app/content/reference_docs/
colorimetrie_palettes_12_saisons.md` pour la méthode, la source, et ce
qui reste à valider avec Clea. Codes hex extraits par échantillonnage de
pixels (pas à l'œil) depuis la charte de référence « THE 12 SEASONS OF
COLOR » fournie par Clea — beaucoup plus fiables que la première version
de ce fichier (estimation visuelle), mais toujours une seule source, pas
encore comparée à un vrai nuancier ni validée côté produit.

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
    "Light Spring": [
        "#B294C6", "#BADEB8", "#F3B785", "#B5D7F2", "#FEF2C0", "#F4ABA5", "#FBF4E1", "#D7C5AD", "#A6835B",
    ],
    "Warm Spring": [
        "#357A7F", "#42875A", "#89B053", "#51B09C", "#FAE274", "#EC665B", "#FBFAE8", "#CB954F", "#99633F",
    ],
    "Bright Spring": [
        "#7F53A2", "#C8D464", "#F9CD54", "#4B73B9", "#45925C", "#EA3627", "#D7C5AF", "#838383", "#5E3B28",
    ],
    # Été (froid, clair, doux)
    "Light Summer": [
        "#4470B7", "#5CBFAA", "#DB448B", "#A999CA", "#D6EDDD", "#F2B7D3", "#FBF7C7", "#708AC7", "#A2A6A9",
    ],
    "Cool Summer": [
        "#4496BB", "#44958C", "#C34B71", "#8BBDE0", "#6EC1A7", "#D072A4", "#ADB9DF", "#FEFBDC", "#376098",
    ],
    "Soft Summer": [
        "#566991", "#658385", "#955F6F", "#877A8C", "#54756A", "#DEA8B6", "#FBEFC5", "#D2CAC8", "#979B9E",
    ],
    # Automne (chaud, profond, mat)
    "Soft Autumn": [
        "#985542", "#D4A39E", "#ECC288", "#646176", "#7C99AB", "#99C8C2", "#656F54", "#706F50", "#969674",
    ],
    "Warm Autumn": [
        "#B54A28", "#E48833", "#FBAE54", "#764524", "#C83B29", "#D05627", "#505831", "#4A7C41", "#617434",
    ],
    "Dark Autumn": [
        "#49140E", "#913921", "#C97D4C", "#1F3C2A", "#4A7152", "#616229", "#15313F", "#285D6F", "#306FA4",
    ],
    # Hiver (froid, profond, éclatant)
    "Cool Winter": [
        "#31398E", "#6C3590", "#CC2C38", "#42926B", "#C54A78", "#F1C5DC", "#3859AA", "#878E94", "#1C2A4F",
    ],
    "Dark Winter": [
        "#421E4A", "#7D162B", "#AC2D4B", "#112C27", "#317163", "#B44D82", "#1D4356", "#408DC1", "#296170",
    ],
    "Bright Winter": [
        "#2F3492", "#4C9F75", "#DA4040", "#74C3EE", "#E9E858", "#E53892", "#E1F2FC", "#656366", "#000000",
    ],
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
