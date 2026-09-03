/**
 * Direction visuelle Shiori : fond ivoire chaud, encre noire, accent
 * rouge sceau. Typographie serif japonisante (Shippori Mincho) pour
 * les titres, sans-serif neutre (IBM Plex Sans) pour l'interface.
 * Esprit "fiche de bibliothèque" — pas de style SaaS générique :
 * cartes avec bordures fines, peu d'ombres, hiérarchie typographique
 * marquée plutôt que de la couleur partout.
 */

export const colors = {
  background: "#F4EFE3",
  backgroundAlt: "#EDE5D2",
  surface: "#FBF8F1",
  ink: "#211D19",
  inkMuted: "#5A5148",
  inkFaint: "#8C8172",
  seal: "#9C3B2E",
  sealMuted: "#C97D6C",
  border: "#DCD2BC",
  success: "#4C6B4F",
  warning: "#B08328",
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const radii = {
  sm: 2,
  md: 6,
  lg: 10,
  pill: 999,
};

export const fonts = {
  serif: "ShipporiMincho_400Regular",
  serifSemiBold: "ShipporiMincho_600SemiBold",
  serifBold: "ShipporiMincho_700Bold",
  sans: "IBMPlexSans_400Regular",
  sansMedium: "IBMPlexSans_500Medium",
  sansSemiBold: "IBMPlexSans_600SemiBold",
};

export const typography = {
  displayTitle: { fontFamily: fonts.serifBold, fontSize: 30, color: colors.ink },
  screenTitle: { fontFamily: fonts.serifSemiBold, fontSize: 24, color: colors.ink },
  cardTitle: { fontFamily: fonts.serif, fontSize: 17, color: colors.ink },
  label: {
    fontFamily: fonts.sansSemiBold,
    fontSize: 11,
    color: colors.inkFaint,
    letterSpacing: 1.2,
  },
  body: { fontFamily: fonts.sans, fontSize: 15, color: colors.ink },
  bodyMuted: { fontFamily: fonts.sans, fontSize: 14, color: colors.inkMuted },
  caption: { fontFamily: fonts.sans, fontSize: 12, color: colors.inkFaint },
  button: { fontFamily: fonts.sansSemiBold, fontSize: 15, color: colors.surface },
};
