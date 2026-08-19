/**
 * Micro-copy centralisée — respecte la charte de ton "reveal, not transform"
 * (docs/CLAUDE.md § Règles de ton non-négociables). Tout texte visible par
 * l'utilisatrice doit passer par ce fichier, jamais en dur dans un écran,
 * pour garder le ton cohérent et auditable en un seul endroit.
 *
 * Rappel des règles :
 * - jamais "avant/après", jamais de vocabulaire correctif
 * - on révèle, on met en lumière, on explore — jamais "on corrige"
 */

export const microcopy = {
  onboarding: {
    welcomeTitle: "Bienvenue",
    welcomeBody:
      "Reveal You t'aide à découvrir ce qui te définit déjà — pas à devenir quelqu'un d'autre.",
    ctaStart: "Commencer mon diagnostic",
  },
  pillars: {
    physique: "Physique",
    mental: "Mental",
    organisation: "Organisation",
    finances: "Finances / Carrière",
    comingSoon: "Bientôt disponible",
  },
  colorimetrie: {
    intro: "Quelques questions pour révéler ta palette de couleurs.",
    resultTitle: "Ta saison colorielle",
    // Affiché quand confiance === "faible" (undertone neutre, ou lecture
    // photo jugée incertaine — voir backend/app/content/reference_docs/
    // colorimetrie_saisons_brouillon.md). Ton "reveal not transform" :
    // jamais présenté comme un doute négatif.
    lowConfidenceNote: "Une première approche à affiner avec toi — on continue de la préciser.",
    photoLinkLabel: "Ou prends 2 photos pour un résultat plus précis",
    photoIntro: "Deux photos de ton visage pour lire directement tes teintes naturelles.",
    photoGuidance:
      "Pour un résultat plus fiable : lumière naturelle, sans maquillage ni filtre si possible. Deux photos dans des conditions un peu différentes (par exemple à deux moments de la journée) aident à confirmer la lecture.",
    photoCta: "Révéler ma palette",
    conseilsStyleTitle: "Quelques pistes de style",
  },
  morphologie: {
    captureIntro: "Une photo et quelques mesures pour révéler ta silhouette.",
    resultTitle: "Ta silhouette",
    formeVisageTitle: "Ta forme de visage",
    // Affiché seulement si la classification forme du visage a échoué côté
    // backend alors que la silhouette a réussi — voir diagnostics.py.
    formeVisageUnavailable: "On n'a pas pu lire ta forme de visage cette fois-ci — réessaie plus tard.",
    conseilsStyleTitle: "Quelques pistes de style",
    formeYeuxTitle: "Ton regard",
    formeYeuxUnavailable: "On n'a pas pu lire la forme de tes yeux cette fois-ci — réessaie plus tard.",
    conseilsMaquillageTitle: "Quelques pistes de maquillage",
    sourcilsTitle: "Tes sourcils",
    sourcilsUnavailable: "On n'a pas pu lire la forme de tes sourcils cette fois-ci — réessaie plus tard.",
  },
  cheveux: {
    // Déclaratif uniquement (pas de photo) — décision produit, voir
    // backend/app/domain/physique/cheveux/nature_cheveux.py.
    intro: "Deux questions pour révéler la nature de tes cheveux et les gestes qui l'accompagnent.",
    stepFamilleTitle: "Quelle est la texture générale de tes cheveux ?",
    stepSousTypeTitle: "Et plus précisément ?",
    cta: "Révéler ma nature de cheveux",
    resultTitle: "Ta nature de cheveux",
    conseilsTitle: "Quelques gestes pour en prendre soin",
    // Familles (méthode André Walker, type 1 à 4).
    familles: {
      "1": { label: "Type 1 — Raides", helper: "Pas d'ondulation ni de boucle, une texture lisse de la racine aux pointes." },
      "2": { label: "Type 2 — Ondulés", helper: "Un léger « S », entre le raide et le bouclé." },
      "3": { label: "Type 3 — Bouclés", helper: "Des boucles bien définies, en spirale." },
      "4": { label: "Type 4 — Crépus", helper: "Un motif très serré, avec du retrait (« shrinkage »)." },
    },
    // Sous-types (A/B/C) au sein de chaque famille.
    sousTypes: {
      "1A": "Très raides et fins, sans volume naturel.",
      "1B": "Raides, avec un peu plus de corps et de volume.",
      "1C": "Raides mais plus épais, quelques mèches ondulent légèrement.",
      "2A": "Ondulations légères et détendues.",
      "2B": "Ondulations plus définies à partir de la mi-longueur.",
      "2C": "Ondulations marquées dès la racine, parfois quelques boucles.",
      "3A": "Boucles larges et souples, bien définies.",
      "3B": "Boucles plus serrées, ressort marqué.",
      "3C": "Boucles très serrées et denses.",
      "4A": "Boucles en « S » très serrées, ressort visible.",
      "4B": "Motif en « Z », plus anguleux.",
      "4C": "Motif le plus serré, peu de boucle visible à l'œil nu.",
    },
  },
} as const;
