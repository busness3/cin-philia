import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ShareResultCard } from "../../../../components/ShareResultCard";
import { microcopy } from "../../../../content/microcopy";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";

export function NatureCheveuxResultScreen() {
  const result = useDiagnosticStore((state) => state.natureCheveux);

  if (!result) {
    return (
      <View style={styles.container}>
        <Text style={styles.body}>Aucun résultat pour l'instant.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{microcopy.cheveux.resultTitle}</Text>
      <Text style={styles.type}>{result.type_texture}</Text>
      <Text style={styles.body}>{result.description}</Text>

      {result.conseils_style.length > 0 ? (
        <View style={styles.conseils}>
          <Text style={styles.conseilsTitle}>{microcopy.cheveux.conseilsTitle}</Text>
          {result.conseils_style.map((conseil) => (
            <Text key={conseil} style={styles.conseil}>
              •{"  "}
              {conseil}
            </Text>
          ))}
        </View>
      ) : null}

      <ShareResultCard
        eyebrow={microcopy.share.cheveuxEyebrow}
        headline={result.type_texture}
        detail={sousTypeLabel(result.type_texture)}
      />
    </ScrollView>
  );
}

// Libellé court du sous-type pour la carte (ex. "Boucles plus serrées,
// ressort marqué.") — la description complète est trop longue pour une
// image partagée.
function sousTypeLabel(typeTexture: string): string | undefined {
  return (microcopy.cheveux.sousTypes as Record<string, string>)[typeTexture];
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.textMuted },
  type: { ...typography.title, color: colors.text },
  body: { ...typography.body, color: colors.text },
  conseils: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
    marginTop: spacing.lg,
  },
  conseilsTitle: { ...typography.body, color: colors.text, fontWeight: "600" },
  conseil: { ...typography.body, color: colors.textMuted },
});
