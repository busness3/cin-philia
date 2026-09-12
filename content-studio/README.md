# Content Studio — montage vidéo TikTok

Système de montage vidéo réutilisable (Python + ffmpeg) pour produire tes
vidéos TikTok à partir de tes rushs et d'une config par série : sous-titres
synchronisés et stylables, titres animés, overlays, musique/SFX depuis ta
bibliothèque, transitions entre séquences — chaque série avec sa propre
direction artistique, cohérente avec ton identité TikTok globale.

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

52 tests couvrent toutes les briques (config, normalisation, sous-titres,
titres/overlays, audio, transitions, pipeline complet) sur des clips générés
à la volée — pas besoin de vrais rushs pour lancer les tests.

## Structure du projet

```
content-studio/
├── configs/
│   ├── global.yaml           identité TikTok globale (résolution, watermark,
│   │                         couleurs de marque, zone sûre, loudness...)
│   └── series/*.yaml         direction artistique par série (couleurs, typo,
│                             style des sous-titres, rythme, ambiance audio)
├── episodes/*.yaml           un fichier par vidéo : quels rushs, dans quel
│                             ordre, accroche/overlays/sfx spécifiques
├── sounds/
│   ├── music/, sfx/          tes fichiers audio (à déposer toi-même)
│   └── index.yaml            associe des clés lisibles (mood, id sfx) aux fichiers
├── assets/
│   ├── fonts/                tes polices .ttf/.otf (nom de fichier = nom
│   │                         utilisé dans les configs, sans extension)
│   └── logo/                 logo/watermark image
├── rushs/                    tes fichiers vidéo bruts (non versionné, à créer)
├── out/                      vidéos rendues (non versionné)
└── src/content_studio/       le code
```

## Utiliser

```bash
# lister les séries configurées
python -m content_studio.cli list-series

# valider une config de série
python -m content_studio.cli check-config diagnostic_serie

# rendre un épisode
python -m content_studio.cli render episodes/exemple_diagnostic_serie.yaml

# garder les fichiers intermédiaires (debug : chaque étape en fichier séparé)
python -m content_studio.cli render episodes/mon_episode.yaml --keep-intermediates
```

Un épisode (`episodes/*.yaml`) décrit une vidéo précise : quels rushs, dans
quel ordre, avec quelle accroche et quels overlays/sfx propres à CETTE vidéo.
Toute la direction artistique (couleurs, typo, rythme...) vient de la config
de la série — voir `episodes/exemple_diagnostic_serie.yaml` pour un gabarit
commenté à copier.

## Les 4 séries

| Série | Fichier config | Ambiance | Sous-titres | Rythme |
|---|---|---|---|---|
| Diagnostic Série | `diagnostic_serie.yaml` | Punchy, contrastée (rouge/noir) | 3 mots, MAJUSCULES, pop, mot actif surligné | Coupes franches, plans courts (1.2–3.5s) |
| Vlogs | `vlogs.yaml` | Chaleureuse, crème/ambre | 2 mots, casse normale, fondu doux | Fondus, plans longs (3–8s) |
| Tests Restos | `tests_restos.yaml` | Appétissante, moutarde/brun, cadre signature | 3 mots, MAJUSCULES, pop | Zoom, plans moyens (1.5–4s) |
| Je lis je regarde je vous en parle | `je_lis_je_regarde.yaml` | Sobre, bleu-vert/crème, carnet de lecture | 4 mots, casse normale, fondu | Le plus lent (2.5–6s) |

Toutes les valeurs sont des **placeholders de départ** pensés pour être
distincts et cohérents entre eux — ouvre le fichier YAML de la série et
change ce que tu veux (couleurs en `#RRGGBB`, tailles en pixels, etc.), aucun
besoin de toucher au code. Le fallback : une couleur non précisée dans une
série retombe sur `identite.couleurs_marque` de `configs/global.yaml`.

## Ajouter tes polices

Dépose le fichier `.ttf`/`.otf` dans `assets/fonts/`, nommé exactement comme
la valeur `police:` utilisée dans les configs (ex: `Montserrat-Bold.ttf` pour
`police: Montserrat-Bold`). Tant qu'une police n'est pas fournie, le système
retombe automatiquement sur une police système de secours (pas de plantage,
juste un rendu provisoire).

## Ajouter ta bibliothèque de sons

1. Dépose tes fichiers dans `sounds/music/` et `sounds/sfx/`
2. Référence-les dans `sounds/index.yaml` :
   - musique : par **mood** (`energique`, `chill`, `gourmand`, `calme`...),
     une ou plusieurs pistes par mood — une est piochée au hasard à chaque
     rendu
   - sfx : par **id** court (`whoosh_court`, `pop`, `ding`...)
3. Une série pointe vers un mood par défaut (`audio.mood_musique` dans sa
   config) ; un épisode peut forcer une piste précise (`audio.musique`) ou
   déclencher un sfx à un instant donné (`audio.sfx`, dans `episodes/*.yaml`)

Tant que la bibliothèque n'est pas remplie, le rendu se poursuit sans
musique/sfx (juste un message dans les logs) — rien ne bloque le reste du
pipeline.

## Sous-titres automatiques

`sous_titres: auto` transcrit l'audio du rush via [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
(modèle `small`, français). Le modèle est téléchargé automatiquement au
premier lancement (connexion internet nécessaire cette fois-là seulement,
puis mis en cache localement). Si la transcription échoue (pas de réseau,
modèle indisponible...), le pipeline continue sans sous-titres sur cette
séquence plutôt que de planter.

Alternative : `sous_titres: chemin/vers/fichier.srt` si tu as déjà un script
écrit à l'avance ou des sous-titres exportés d'ailleurs. `sous_titres: aucun`
pour ne rien afficher.

## Limitations connues

- **Titres longs** : `render_title_card` centre le texte sur une seule ligne
  par défaut ; un titre trop long déborde du cadre. Insère un retour à la
  ligne manuel dans le texte pour le répartir toi-même sur plusieurs lignes.
- **Transcription auto** : nécessite une connexion internet au premier
  lancement (téléchargement du modèle Whisper, ~250 Mo pour `small`).
- **ffmpeg requis sur la machine**, en plus des dépendances Python.

## Étendre le système

- **Nouvelle série** : copie un fichier de `configs/series/`, change les
  couleurs/typo/rythme, donne-lui un nouveau nom de fichier (= son id).
- **Nouvelle brique** (ex: un nouveau type de transition, un nouveau style
  d'animation de sous-titres) : chaque brique est un module indépendant et
  testé (`normalize.py`, `subtitles.py`, `titles.py`, `overlays.py`,
  `audio.py`, `transitions.py`) — `pipeline.py` les enchaîne. Ajoute la
  fonctionnalité dans le module concerné, un test dans `tests/`, puis
  branche-la dans `pipeline.py` si besoin.
