# Manga Tracker — Backend

API + job planifié pour l'app de suivi de lecture manga/manhwa/manhua.
C'est la partie qu'une simple appli mobile locale ne peut pas faire
seule : interroger des API externes côté serveur, comparer l'état des
chapitres dans le temps, et pousser des notifications même quand
l'app est fermée.

## Ce que fait ce backend

1. **Recherche & métadonnées** (`GET /api/search`, `GET /api/manga/:id`)
   — combine [l'API MangaDex](https://api.mangadex.org/docs/) (source
   principale : couvertures officielles, flux de chapitres) et
   [l'API AniList](https://anilist.co/graphiql) (complément éditorial).
2. **Suivi des nouveaux chapitres** (`src/jobs/checkNewChapters.ts`) —
   job planifié (par défaut toutes les heures, `node-cron`) qui, pour
   chaque titre suivi en ligne par au moins un utilisateur, interroge
   le flux de chapitres MangaDex, compare au dernier chapitre connu
   (`manga_titles.last_known_chapter`) et enregistre les nouveautés.
3. **Notifications push** (`src/lib/expoPush.ts`) — envoi via l'API
   Expo Push dès qu'une nouveauté est détectée.
4. **Compte utilisateur + base de données** — délégués à **Supabase**
   (Postgres + Auth). Ce backend n'implémente pas sa propre gestion de
   comptes : l'app mobile s'authentifie directement auprès de Supabase
   et lit/écrit sa bibliothèque personnelle via des policies RLS (voir
   `supabase/schema.sql`). Le backend n'intervient, avec la clé
   `service_role`, que pour le job de suivi (lecture toutes
   bibliothèques confondues, écriture des notifications).

## ⚠️ Limite importante — à lire absolument

**Le lien de lecture personnel** (le site précis où l'utilisatrice lit
un chapitre, par ex. un site de scan donné) **reste saisi manuellement
à l'ajout d'un titre.** Ni MangaDex ni AniList n'hébergent ni
n'indexent ces sites de lecture — ces API ne fournissent que les
métadonnées (titre, couverture, liste des chapitres parus).

Conséquence directe : **la détection automatique de nouveaux
chapitres ne fonctionne que pour les titres identifiés sur MangaDex**
(`trackable: true` dans les résultats de recherche). Un titre trouvé
uniquement via AniList, ou ajouté en support "papier", n'est jamais
vérifié par le job planifié — dans le cas du papier, c'est un choix
volontaire (aucune source à surveiller pour un livre physique) ; dans
le cas d'AniList seul, c'est une limite de couverture de l'API.

## Architecture des données (Supabase)

Voir `supabase/schema.sql` pour le détail complet (tables + policies
RLS). Résumé :

- `manga_titles` — cache partagé, un titre MangaDex = une ligne, quel
  que soit le nombre d'utilisateurs qui le suivent (évite d'interroger
  MangaDex une fois par utilisateur pour le même titre).
- `library_entries` — bibliothèque personnelle (une ligne par titre
  ajouté par un utilisateur : chapitre en cours, lien de lecture,
  support, statut, notes).
- `notifications` — nouveautés détectées par le job, une ligne par
  utilisateur concerné.
- `push_tokens` — jetons Expo Push par utilisateur/appareil.

## Démarrer en local

```bash
npm install
cp .env.example .env
# renseigner SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY (dashboard Supabase > Settings > API)
npm run dev
```

Le serveur écoute sur `http://localhost:3000` par défaut, et démarre
aussi le scheduler (job de suivi toutes les heures par défaut,
`CHAPTER_CHECK_CRON`).

Pour lancer un seul passage du job sans garder le serveur actif :

```bash
npm run check-chapters
```

## Mettre en place la base Supabase

1. Créer un projet sur [supabase.com](https://supabase.com).
2. Dans l'éditeur SQL du projet, exécuter le contenu de
   `supabase/schema.sql`.
3. Activer l'authentification par e-mail/mot de passe (Authentication
   > Providers > Email) — c'est ce que l'app mobile utilise.
4. Récupérer dans Settings > API : `Project URL`, la clé `anon` (pour
   le mobile) et la clé `service_role` (pour ce backend, dans `.env`
   uniquement — jamais côté mobile).

## Déploiement

N'importe quel hébergeur Node.js qui garde un process persistant
(Render, Railway, Fly.io...) convient, tant qu'il exécute `npm run
build && npm start` et garde le process actif pour que `node-cron`
puisse tourner. Alternative : déployer uniquement l'API (recherche)
sur une plateforme serverless, et faire tourner `npm run
check-chapters` comme job cron externe (cron du fournisseur, GitHub
Actions planifié...).

## Routes

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | Vérification de disponibilité |
| GET | `/api/search?q=...` | Recherche combinée MangaDex + AniList |
| GET | `/api/manga/:mangadexId` | Détail d'un titre + derniers chapitres |
| GET | `/api/manga/:mangadexId/chapters` | Derniers chapitres seuls |

Tout le reste (bibliothèque, notifications, jetons push) est lu/écrit
directement par l'app mobile dans Supabase, protégé par RLS — pas
besoin de dupliquer ces routes ici.
