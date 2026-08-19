import { ScrollView, StyleSheet, Text, View } from "react-native";

import { microcopy } from "../../../../content/microcopy";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";

export function ColorimetrieResultScreen() {
  const result = useDiagnosticStore((state) => state.colorimetrie);

  if (!result) {
    return (
      <View style={styles.container}>
        <Text style={styles.body}>Aucun résultat pour l'instant.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{microcopy.colorimetrie.resultTitle}</Text>
      <Text style={styles.season}>{result.saison}</Text>
      {result.sous_saison ? <Text style={styles.subSeason}>{result.sous_saison}</Text> : null}
      {result.confiance === "faible" ? (
        <Text style={styles.note}>{microcopy.colorimetrie.lowConfidenceNote}</Text>
      ) : null}

      <View style={styles.palette}>
        {result.palette.map((hex) => (
          <View key={hex} style={[styles.swatch, { backgroundColor: hex }]} />
        ))}
      </View>

      {result.justification ? <Text style={styles.justification}>{result.justification}</Text> : null}

      {result.conseils_style.length > 0 ? (
        <View style={styles.conseils}>
          <Text style={styles.conseilsTitle}>{microcopy.colorimetrie.conseilsStyleTitle}</Text>
          {result.conseils_style.map((conseil) => (
            <Text key={conseil} style={styles.conseil}>
              •{"  "}
              {conseil}
            </Text>
          ))}
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.textMuted },
  season: { ...typography.title, color: colors.text },
  subSeason: { ...typography.body, color: colors.textMuted },
  note: { ...typography.caption, color: colors.textMuted, marginTop: spacing.xs },
  body: { ...typography.body, color: colors.textMuted },
  palette: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.lg },
  justification: { ...typography.body, color: colors.textMuted, marginTop: spacing.lg, fontStyle: "italic" },
  // Bordure défensive : certaines couleurs de palette (ex. blanc/glacier)
  // se fondraient sinon dans le fond clair de l'app.
  swatch: { width: 48, height: 48, borderRadius: radii.sm, borderWidth: 1, borderColor: colors.border },
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
