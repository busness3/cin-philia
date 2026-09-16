# Content Studio — montage vidéo TikTok « petit boucan »

Système de montage vidéo réutilisable (Python + ffmpeg) pour produire les
vidéos TikTok du compte **petit boucan** à partir des rushs et d'une config
par série : sous-titres synchronisés, titre incrusté en ouverture/sortie,
couverture générée automatiquement, musique/SFX depuis la bibliothèque,
transitions entre séquences — toute l'identité visuelle vient d'un seul
document de DA globale, chaque série n'y ajoute que sa couleur d'accent.

## Principe : DA globale, série = accent seulement

Toute la direction artistique (palette crème/chocolat, typo Archivo, style
des sous-titres, gabarit de couverture, timing d'ouverture/sortie) est
définie **une seule fois** dans `configs/global.yaml` et s'applique à toutes
les vidéos, quelle que soit la série. Une config de série
(`configs/series/*.yaml`) ne peut surcharger que :
- sa **couleur d'accent** (`accent: "#RRGGBB"`)
- des métadonnées de production informatives (tenue, décor, structure de
  script, CTA de sortie...) qui n'affectent pas directement le rendu, sauf
  `cta_sortie` (texte affiché dans le bandeau de sortie).

Rien d'autre n'est surchargeable par série — c'est voulu : voir le document
de DA globale pour le détail des règles.

## Installer

```bash
cd content-studio
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Il faut aussi **ffmpeg** installé sur la machine (pas juste le paquet Python) :

```bash
brew install ffmpeg        # Mac
sudo apt install ffmpeg    # Linux
```

## Tester que tout fonctionne

```bash
python3 -m pytest tests/ -v
```

62 tests couvrent toutes les briques (config, normalisation, sous-titres,
bandeau titre, couverture, audio, transitions, pipeline complet) sur des
clips générés à la volée — pas besoin de vrais rushs pour lancer les tests.

## Structure du projet

```
content-studio/
├── configs/
│   ├── global.yaml           LE document de DA : palette, typo, sous-titres,
│   │                         gabarit de couverture, timing, technique
│   └── series/*.yaml         accent + métadonnées de production par série
├── episodes/*.yaml           un fichier par vidéo : rushs, accroche, overlays
├── sounds/
│   ├── music/, sfx/          fichiers audio (à déposer soi-même)
│   └── index.yaml            associe des clés lisibles (mood, id sfx) aux fichiers
├── assets/
│   ├── fonts/                Archivo-Medium.ttf + ArchivoNarrow-SemiBold.ttf
│   │                         (Google Fonts, licence SIL OFL, fournies avec le repo)
│   └── logo/                 logo/watermark image (optionnel, désactivé par défaut)
├── rushs/                    fichiers vidéo bruts (non versionné, à créer)
├── out/                      vidéos + couvertures rendues (non versionné)
└── src/content_studio/       le code
```

## Utiliser

```bash
# lister les séries configurées
python -m content_studio.cli list-series

# valider une config de série
python -m content_studio.cli check-config diagnostic_serie

# rendre un épisode (génère la vidéo ET sa couverture PNG)
python -m content_studio.cli render episodes/exemple_diagnostic_serie.yaml

# garder les fichiers intermédiaires (debug : chaque étape en fichier séparé)
python -m content_studio.cli render episodes/mon_episode.yaml --keep-intermediates
```

Un épisode (`episodes/*.yaml`) décrit une vidéo précise : quels rushs, dans
quel ordre, avec quel titre d'ouverture et quels overlays/sfx propres à
CETTE vidéo. Voir `episodes/exemple_diagnostic_serie.yaml` pour un gabarit
commenté à copier.

## Les 4 séries

| Série | Fichier config | Accent | CTA de sortie |
|---|---|---|---|
| Diagnostic Série | `diagnostic_serie.yaml` | `#D42A2A` rouge franc | "Ton avis en commentaire ?" |
| Vlogs Dakar | `vlogs_dakar.yaml` | `#C96B4A` terracotta | "Vous voulez voir la suite ?" |
| Tests Restos | `tests_restos.yaml` | `#D89A1E` ocre | "Le nom du resto est en légende !" |
| Je lis je regarde je vous en parle | `je_lis_je_regarde.yaml` | `#8C4A3E` brique | "Vous l'avez lu/vu ? Dites-moi en commentaire." |

Les 3 premiers accents viennent directement du document de DA globale.
Celui de la 4e série (absente du document initial) est un choix par défaut
respectant les mêmes règles (famille chaude, distinct des 3 autres et du
chocolat) — à valider/ajuster librement dans son fichier YAML.

## Ce que fait le pipeline, dans l'ordre

1. **Par séquence** : normalisation du rush (recadrage au format vertical) →
   sous-titres (transcription auto, SRT fourni, ou aucun) → overlays texte
   ponctuels éventuels.
2. **Assemblage** des séquences avec transitions (cut par défaut).
3. **Bandeau d'ouverture** : titre incrusté sur le plan de début (bandeau
   crème + bloc accent + titre 2 lignes), de `t=0.3s` à `t=2.3s`.
4. **Bandeau de sortie** (optionnel, activable/désactivable dans
   `configs/global.yaml` → `timing.sortie_activee`) : même bandeau, CTA de
   la série, sur les 2 dernières secondes.
5. **Mixage audio** : voix + musique de la bibliothèque (démarre après le
   premier mot détecté par la transcription, jamais avant) + SFX ponctuels,
   avec ducking et normalisation de loudness.
6. **Couverture** : image PNG 1080×1920 générée à côté de la vidéo (même
   bandeau/titre que l'ouverture), à partir d'une frame extraite de la vidéo.

## Sous-titres automatiques

`sous_titres: auto` transcrit l'audio du rush via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
(modèle `small`, français), puis découpe en légendes par **phrases
naturelles** (pas de paquets de mots punchy — DA minimaliste). Le modèle est
téléchargé automatiquement au premier lancement (connexion internet
nécessaire cette fois-là, puis mis en cache localement). Si la transcription
échoue (pas de réseau, modèle indisponible...), le pipeline continue sans
sous-titres sur cette séquence plutôt que de planter, et la musique démarre
avec un délai par défaut (1s) au lieu d'être calée sur le premier mot.

Alternative : `sous_titres: chemin/vers/fichier.srt` si un script est déjà
écrit à l'avance. `sous_titres: aucun` pour ne rien afficher.

## Limites connues (approximations du rendu ffmpeg/libass)

- **Coins arrondis des sous-titres** (12px dans la config) : non appliqués.
  Le rendu (ASS/libass) donne un rectangle net. Un rendu pixel-parfait
  demanderait un fond pré-rendu en image par sous-titre (plus lourd à
  maintenir) — pas fait pour l'instant.
- **Padding des sous-titres** : la config distingue horizontal (24px) et
  vertical (16px), mais ASS n'a qu'une seule valeur de padding — la moyenne
  (20px) est utilisée.
- **Légère "couture"** parfois visible entre les 2 lignes d'un sous-titre
  multi-ligne (le fond crème n'est pas toujours un rectangle parfaitement
  uniforme sur 2 lignes) — limitation connue de libass sur les boîtes
  `BorderStyle=3` multi-lignes.
- **Position du texte du bandeau** (ouverture/sortie/couverture) : calée sur
  la hauteur totale du texte (descendantes incluses), donc la ligne de base
  visuelle est légèrement plus haute que la valeur pixel exacte de la config
  quand le texte contient des lettres à jambage (g, j, p, q, y).
- **Titres longs** : le bandeau accepte 2 lignes ; au-delà, insère un retour
  à la ligne manuel dans le texte pour contrôler la coupure toi-même.
- **ffmpeg requis sur la machine**, en plus des dépendances Python.

## Ajouter ta bibliothèque de sons

1. Dépose tes fichiers dans `sounds/music/` et `sounds/sfx/`
2. Référence-les dans `sounds/index.yaml` :
   - musique : par **mood** (`energique`, `chill`, `gourmand`, `calme`...),
     une ou plusieurs pistes par mood — une est piochée au hasard à chaque
     rendu
   - sfx : par **id** court (`whoosh_court`, `pop`, `ding`...)
3. Chaque série pointe vers un mood par défaut (`audio.mood_musique`) ; un
   épisode peut forcer une piste précise (`audio.musique`) ou déclencher un
   sfx à un instant donné (`audio.sfx`, dans `episodes/*.yaml`).

Tant que la bibliothèque n'est pas remplie, le rendu se poursuit sans
musique/sfx (juste un message dans les logs) — rien ne bloque le pipeline.

## Étendre le système

- **Nouvelle série** : copie un fichier de `configs/series/`, choisis un
  accent chaud non utilisé (règles section 2 du doc de DA), donne-lui un
  nouveau nom de fichier (= son id). Rien d'autre à changer.
- **Ajuster la DA globale** (couleurs de base, typo, timing, gabarit de
  couverture) : tout se fait dans `configs/global.yaml`, aucun besoin de
  toucher au code.
- **Nouvelle brique** : chaque étape est un module indépendant et testé
  (`normalize.py`, `subtitles.py`, `band.py`, `cover.py`, `overlays.py`,
  `audio.py`, `transitions.py`) — `pipeline.py` les enchaîne.
