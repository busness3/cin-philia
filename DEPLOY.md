# Déploiement — Reveal You

Ce document explique comment passer du prototype (qui tourne seulement
sur cette machine de dev) à une version accessible sur ton téléphone,
en dehors de cet environnement de développement.

Deux parties, indépendantes : **le backend** (API) doit être en ligne
en premier, car l'app mobile a besoin de son adresse publique.

Tout ce qui pouvait être préparé dans le code l'a été (fichiers de config
ci-dessous). Il reste des actions que **seule toi** peux faire, car elles
demandent de créer des comptes / d'entrer tes identifiants — listées en
gras à chaque étape.

---

## 1. Backend — héberger l'API (Railway)

Le code est prêt pour Railway (`backend/Procfile`, `backend/runtime.txt`).
Railway sait déjà comment lancer une app Python/FastAPI à partir de ces
fichiers.

1. **Créer un compte sur [railway.app](https://railway.app)** (gratuit
   pour démarrer, se connecte avec GitHub).
2. **Créer un nouveau projet → "Deploy from GitHub repo"** → sélectionner
   ce repo (`cin-philia`), dossier racine `backend/`.
   - Si Railway demande un "root directory", indiquer `backend`.
3. **Ajouter les variables d'environnement** dans l'onglet "Variables" du
   service Railway :
   - `ANTHROPIC_API_KEY` → ta vraie clé API Claude (celle utilisée pour
     les diagnostics colorimétrie/silhouette)
   - `DATABASE_URL` → laisser vide pour l'instant, SQLite par défaut
     suffit pour tester (Railway fournit un disque persistant limité ;
     pour une vraie mise en prod avec plusieurs utilisatrices, il vaudra
     mieux brancher une vraie base Postgres — Railway peut aussi
     l'héberger en un clic le moment venu, mais ce n'est pas nécessaire
     pour tester la V1)
   - `ENVIRONMENT` → `production`
   - `CORS_ALLOW_ORIGINS` → laisser `*` pour l'instant (l'app mobile
     n'utilise pas de cookies, donc ce n'est pas un risque de sécurité
     ici — à restreindre plus tard si un site web est ajouté)
4. Railway déploie automatiquement. Une fois terminé, **noter l'URL
   publique** donnée par Railway (ex. `https://reveal-you-backend-production.up.railway.app`)
   — onglet "Settings" → "Networking" → "Generate Domain" si elle n'est
   pas déjà visible.
5. Vérifier que ça marche : ouvrir `<ton-url>/docs` dans un navigateur —
   la doc interactive de l'API doit s'afficher.

**Ce qui est déjà prêt dans le repo :** `backend/Procfile` (commande de
démarrage), `backend/runtime.txt` (version Python), `backend/requirements.txt`
(dépendances), CORS activé dans `backend/app/main.py`.

---

## 2. Mobile — construire l'app (Expo / EAS)

1. **Créer un compte sur [expo.dev](https://expo.dev)** (gratuit).
2. Sur ta machine (pas dans cet environnement — voir note plus bas),
   installer l'outil EAS et te connecter :
   ```bash
   npm install -g eas-cli
   cd mobile
   eas login
   ```
3. **Lier le projet à ton compte Expo** :
   ```bash
   eas init
   ```
   Cette commande crée un `projectId` propre à ton compte et modifie
   automatiquement `mobile/app.json` — c'est une identité de compte, donc
   je ne peux pas la générer à ta place.
4. Renseigner l'URL du backend (celle notée à l'étape 1) dans
   `mobile/eas.json` : remplacer les deux occurrences de
   `REMPLACER-PAR-URL-RAILWAY.up.railway.app` par ta vraie URL Railway
   (profils `preview` et `production`).
5. Construire un build de test à installer directement sur ton téléphone :
   ```bash
   eas build --profile preview --platform ios      # ou android
   ```
   EAS fournit un lien de téléchargement/QR code à la fin — installe le
   build directement sur ton téléphone (pas besoin de passer par
   l'App Store / Play Store pour tester).

**Ce qui est déjà prêt dans le repo :** `mobile/eas.json` (profils de
build), le code lit déjà `EXPO_PUBLIC_API_BASE_URL` pour savoir où
trouver le backend (`mobile/src/services/api.ts`).

### Pourquoi pas depuis cet environnement de développement ?

`eas build` et `eas login` demandent une authentification interactive à
ton compte Expo (email/mot de passe ou navigateur) — je ne peux pas le
faire à ta place, et cet environnement n'a de toute façon pas accès à
un vrai navigateur ou téléphone pour tester le résultat. Ces commandes
sont à lancer depuis ton ordinateur, avec le repo cloné en local
(`git clone`, puis `git checkout` sur la branche de travail).

---

## Résumé — ce qui reste uniquement à toi

1. Créer le compte Railway + connecter le repo + renseigner
   `ANTHROPIC_API_KEY` dans les variables d'environnement.
2. Créer le compte Expo + `eas login` + `eas init` (génère ton
   `projectId`) + lancer le build depuis ta machine.
3. Reporter l'URL Railway obtenue à l'étape 1 dans `mobile/eas.json`
   avant de lancer le build.

Tout le reste (configuration, fichiers de déploiement, code) est déjà
en place dans le repo.
