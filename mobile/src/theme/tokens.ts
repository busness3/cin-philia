/**
 * Design tokens — direction visuelle définie dans docs/CLAUDE.md :
 * palettes chaudes et lumineuses, typographie arrondie, formes organiques.
 * À affiner avec Clea (direction design) — ce sont des valeurs de départ,
 * pas une charte graphique validée.
 */

export const colors = {
  background: "#FDF8F2",
  surface: "#FFFFFF",
  primary: "#E8A87C",
  primaryDark: "#C97F52",
  accent: "#D4A5A5",
  text: "#3D3229",
  textMuted: "#8A7B6C",
  border: "#EFE4D6",
  comingSoon: "#E5DFD5",
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const radii = {
  sm: 8,
  md: 16,
  lg: 24,
  pill: 999,
};

export const typography = {
  title: { fontSize: 28, fontWeight: "600" as const },
  subtitle: { fontSize: 18, fontWeight: "500" as const },
  body: { fontSize: 15, fontWeight: "400" as const },
  caption: { fontSize: 13, fontWeight: "400" as const },
};
