# Content Studio — montage vidéo TikTok

Système de montage vidéo réutilisable (Python + ffmpeg) pour produire des
vidéos TikTok à partir de rushs bruts et d'une config par série.

**⚠️ En construction, brique par brique.** Voir l'avancement ci-dessous.
La documentation complète (installation, structure des configs, guide par
série) sera ajoutée une fois toutes les briques posées et testées.

## Avancement

- [x] Squelette projet + config (YAML/pydantic) — `configs/global.yaml` +
      `configs/series/*.yaml`
- [x] Normalisation des rushs (`src/content_studio/normalize.py`)
- [ ] Sous-titres synchronisés stylables (transcription auto + burn-in)
- [ ] Titres animés / accroches
- [ ] Overlays (texte, cadres, watermark)
- [ ] Musique + SFX depuis bibliothèque
- [ ] Transitions entre séquences
- [ ] Orchestrateur + CLI
- [ ] Configs des 4 séries (Diagnostic Série, vlogs, tests restos, "je lis
      je regarde je vous en parle")

## Installer (dev)

```bash
cd content-studio
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ffmpeg doit être installé sur la machine (brew install ffmpeg / apt install ffmpeg)
```

## Tests

```bash
python3 -m pytest tests/ -v
```
