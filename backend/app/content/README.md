# Contenu de référence produit

Documents de référence de Clea, utilisés comme source de vérité pour les
prompts de classification (`docs/CLAUDE.md` → "Ne jamais halluciner de
critères typologiques"). Verbatim dans `reference_docs/`, chargés à
l'exécution par le code de classification plutôt que dupliqués en dur.

## Statut par catégorie

- [x] **Silhouette (H/A/V/O/X)** — critères complets reçus et intégrés (`silhouettes_guide_reference.md`). Classification fonctionnelle.
- [ ] **Forme du visage (7 types)** — noms reçus, critères distinctifs toujours non fournis (signalé comme non résolu dans le document source lui-même)
- [ ] **Forme des yeux (9+ types)** — noms + quelques clarifications partielles reçus, critères de repérage complets manquants
- [ ] **Sourcils, type de peau** — noms seulement, pas de logique de classification prévue dessus pour l'instant (pas dans le scope diagnostic V1 défini)
- [ ] **Table saison colorielle** — undertone + contraste + cheveux → saison/sous-saison. Le framework (4 saisons vs 12 sous-saisons, définitions undertone/contraste) est reçu, mais pas la table de correspondance elle-même.

## Décisions produit encore ouvertes (signalées dans le doc source)

- Silhouette : le doc de référence détaille aussi 2 variantes ("8",
  "Diamant/Ovale") en plus des 5 catégories officielles (H/A/V/O/X).
  **Décision par défaut prise pour la V1 : on reste sur les 5 catégories
  officielles.** À confirmer avec Clea si on veut les 7.
- Cheveux : classification complète André Walker (1A-4C) ou version
  simplifiée en 4 catégories pour le MVP ? Pas encore implémenté.
- Nombre de photos demandées à l'utilisatrice (visage seul / visage +
  corps entier) — impacte le flow de capture mobile.
- Niveau de détail colorimétrie pour le MVP (4 saisons ou 12 sous-saisons).

Tant qu'un point reste ouvert, le code correspondant reste en placeholder
explicite plutôt que d'inventer.
