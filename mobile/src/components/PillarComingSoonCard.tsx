import { StyleSheet, Text, View } from "react-native";

import { microcopy } from "../content/microcopy";
import { colors, radii, spacing, typography } from "../theme/tokens";

interface Props {
  pillarName: string;
}

/** Écran affiché pour les 3 piliers pas encore développés (Mental,
 * Organisation, Finances/Carrière) — visibles dans la navigation pour
 * garder la structure produit à 4 piliers visible, mais non cliquables
 * au-delà de cet écran d'attente. Voir docs/CLAUDE.md § Structure produit. */
export function PillarComingSoonCard({ pillarName }: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{pillarName}</Text>
        <Text style={styles.badge}>{microcopy.pillars.comingSoon}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.lg,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    padding: spacing.xl,
    alignItems: "center",
    gap: spacing.sm,
  },
  title: { ...typography.title, color: colors.text },
  badge: {
    ...typography.caption,
    color: colors.textMuted,
    backgroundColor: colors.comingSoon,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: radii.pill,
    overflow: "hidden",
  },
});
