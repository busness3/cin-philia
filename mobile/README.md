# Reveal You — app mobile (prototype)

Expo (React Native + TypeScript). Navigation à 4 piliers dès la V1 — seul
**Physique** est cliquable, les 3 autres affichent un écran "bientôt
disponible" (voir `docs/CLAUDE.md` § Architecture extensible).

## Démarrer

```bash
npm install
npx expo start
```

Configurer l'URL du backend via une variable d'env Expo (sinon
`http://localhost:8000` par défaut) :

```bash
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000 npx expo start
```

## Vérifier les types

```bash
npx tsc --noEmit
```

## Statut

Les écrans de diagnostic (colorimétrie, silhouette) appellent le backend et
gèrent l'erreur "pas encore disponible" tant que les tables/prompts de
classification restent des placeholders côté backend — voir
`backend/app/content/README.md`.

## Confidentialité

La photo choisie par l'utilisatrice n'est jamais copiée dans un stockage
applicatif persistant : elle est lue une seule fois pour l'upload vers le
backend (`src/services/api.ts`), qui lui-même ne la persiste jamais (voir
`docs/CLAUDE.md`).
