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
  },
  morphologie: {
    captureIntro: "Une photo et quelques mesures pour révéler ta silhouette.",
    resultTitle: "Ta silhouette",
  },
} as const;
