# Reveal You

Application de développement personnel — pilier Physique (V1).
Voir [`docs/CLAUDE.md`](docs/CLAUDE.md) pour les spécifications produit complètes.

## Structure du repo

```
reveal-you/
├── backend/     # API FastAPI — diagnostic colorimétrie + morphologie
├── mobile/      # App mobile Expo (React Native + TypeScript)
└── docs/        # Spécifications produit
```

## Statut : prototype

Le backend et l'app mobile fonctionnent de bout en bout pour les 2
fonctionnalités V1 : **colorimétrie** (formulaire ou 2 photos) et
**silhouette** (2 photos, face + profil). La classification réelle est
en place, basée sur les documents de référence de Clea. Certains éléments
restent des brouillons à valider par Clea avant mise en prod (table de
correspondance saison colorielle, palettes de couleurs) — voir
[`backend/app/content/README.md`](backend/app/content/README.md) pour le
détail à jour.

Voir [`mobile/README.md`](mobile/README.md) pour démarrer l'app en local,
et [`DEPLOY.md`](DEPLOY.md) pour la mettre en ligne (backend hébergé +
build mobile installable sur téléphone).

## Confidentialité — principe non négociable

Aucune photo utilisateur n'est jamais persistée (disque, base, logs). Le
traitement se fait en mémoire, le temps de l'appel à l'API de
classification, puis la photo est immédiatement jetée. Seuls les résultats
dérivés (saison, type de silhouette...) sont stockés. Détail dans
[`docs/CLAUDE.md`](docs/CLAUDE.md#-principes-de-confidentialité-des-données-ajouté-en-session).

## Démarrer le backend en local

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

API disponible sur `http://localhost:8000` — doc interactive sur `/docs`.

```bash
# Lancer les tests
pytest
```
