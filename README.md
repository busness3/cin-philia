# Reveal You

Application de développement personnel — pilier Physique (V1).
Voir [`docs/CLAUDE.md`](docs/CLAUDE.md) pour les spécifications produit complètes.

## Structure du repo

```
reveal-you/
├── backend/     # API FastAPI — diagnostic colorimétrie + morphologie
├── docs/        # Spécifications produit
└── app/         # App mobile (à venir)
```

## Statut : prototype

Le backend est scaffoldé et fonctionnel (santé de l'API, pipeline de
diagnostic en bout en bout), mais **la logique de classification réelle est
en attente des documents de référence de Clea** (types de silhouette,
formes de visage, formes d'yeux, table saison colorielle). Voir
[`backend/app/content/README.md`](backend/app/content/README.md) pour le
détail de ce qui manque.

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
