# Shiori — Manga Tracker (mobile)

App mobile Expo/React Native du tracker de lecture manga/manhwa/manhua.
Voir aussi [`../backend/README.md`](../backend/README.md) pour
la partie serveur (recherche, suivi des nouveaux chapitres, push).

## Fonctionnalités

- **Bibliothèque** triée alphabétiquement, vue liste ou grille (affiches).
- **Fiche par titre** : chapitre en cours, lien de lecture personnalisé,
  support (papier / en ligne), statut, notes.
- **Ajout par recherche** : recherche combinée MangaDex + AniList via le
  backend, sélection d'un résultat → fiche créée automatiquement (titre
  et affiche récupérés, pas de saisie manuelle).
- **Notifications** : liste des nouveaux chapitres détectés par le job
  planifié du backend pour les titres suivis en ligne. Les titres
  "papier" n'y apparaissent jamais (aucune source à surveiller).

## ⚠️ Limite à connaître

Le lien de lecture personnel (le site précis où tu lis un titre) est
**toujours saisi à la main** à l'ajout ou depuis la fiche : ni
MangaDex ni AniList n'hébergent ces sites de scan, seulement les
métadonnées. Le suivi automatique des nouveaux chapitres ne fonctionne
que pour les titres identifiés sur MangaDex (badge « Pas de suivi
auto » affiché sinon dans les résultats de recherche).

## Démarrer en local

```bash
npm install
cp .env.example .env.local
# renseigner EXPO_PUBLIC_SUPABASE_URL, EXPO_PUBLIC_SUPABASE_ANON_KEY
# (même projet Supabase que le backend, clé "anon" cette fois)
# et EXPO_PUBLIC_API_BASE_URL (URL du backend Shiori)
npm start
```

Prérequis : avoir exécuté `supabase/schema.sql` (voir le README du
backend) sur le projet Supabase, et avoir le backend démarré (`npm run
dev` dans `shiori/backend/`) pour que la recherche fonctionne.

## Notifications push

Les push utilisent l'API Expo Push. En développement (Expo Go), la
récupération du jeton peut nécessiter un projet EAS configuré
(`eas init`, puis renseigner `extra.eas.projectId` dans `app.json`) —
sans ça, l'app fonctionne normalement mais sans jeton push enregistré
(log d'avertissement, pas de crash). Voir `src/lib/notifications.ts`.

## Structure

```
src/
├── theme/          # tokens de design (couleurs, typo, espacements)
├── lib/            # clients Supabase + backend, notifications push
├── context/        # AuthContext (session Supabase)
├── navigation/      # RootNavigator (auth stack / tabs / fiches)
├── screens/
│   ├── auth/        # connexion, inscription
│   ├── library/      # bibliothèque, ajout, fiche titre
│   └── notifications/
└── components/      # cartes, boutons, champs, etc.
```

## Direction visuelle

Fond ivoire chaud (`#F4EFE3`), encre noire (`#211D19`), accent rouge
sceau (`#9C3B2E`). Titres en **Shippori Mincho** (serif japonisante),
interface en **IBM Plex Sans**. Cartes façon fiches de bibliothèque —
bordures fines, peu d'ombres — voir `src/theme/tokens.ts`.
