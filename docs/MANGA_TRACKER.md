# Shiori — Manga Tracker

Projet **indépendant** du reste de ce dépôt (« Reveal You », documenté
dans [`CLAUDE.md`](./CLAUDE.md)) : une app de suivi de lecture
manga/manhwa/manhua, en français, vivant dans ses propres dossiers à la
racine pour ne pas interférer avec le code existant :

```
manga-backend/   # API Node/TypeScript — recherche, suivi des chapitres, push
manga-mobile/    # App Expo/React Native
```

## Pourquoi un backend, pas juste une appli locale

Une bibliothèque manga peut se stocker localement, mais deux choses
nécessitent un serveur :

1. **Recherche de titres sans saisie manuelle** — interroger les API
   publiques MangaDex et AniList pour récupérer titre, affiche et
   métadonnées.
2. **Détection de nouveaux chapitres même app fermée** — un job
   planifié doit interroger régulièrement le flux MangaDex, comparer
   au dernier chapitre connu, et pousser une notification.

Détail complet : [`manga-backend/README.md`](../manga-backend/README.md)
et [`manga-mobile/README.md`](../manga-mobile/README.md).

## Limite structurelle à connaître

Le lien de lecture personnel (le site précis où l'utilisatrice lit un
chapitre) n'est fourni ni par MangaDex ni par AniList — ces API ne
donnent que les métadonnées. Il est donc saisi manuellement à l'ajout
d'un titre, et le suivi automatique des nouveaux chapitres ne
fonctionne que pour les titres identifiés sur MangaDex.

## Démarrage rapide

```bash
# 1. Base de données — dans le dashboard Supabase, éditeur SQL :
#    exécuter manga-backend/supabase/schema.sql

# 2. Backend
cd manga-backend
npm install
cp .env.example .env   # SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
npm run dev

# 3. Mobile (autre terminal)
cd manga-mobile
npm install
cp .env.example .env.local   # SUPABASE_URL + clé anon + URL du backend
npm start
```
