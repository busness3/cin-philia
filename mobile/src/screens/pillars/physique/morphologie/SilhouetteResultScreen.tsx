import { StyleSheet, Text, View } from "react-native";

import { microcopy } from "../../../../content/microcopy";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, spacing, typography } from "../../../../theme/tokens";

export function SilhouetteResultScreen() {
  const result = useDiagnosticStore((state) => state.morphologie);

  if (!result) {
    return (
      <View style={styles.container}>
        <Text style={styles.body}>Aucun résultat pour l'instant.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.morphologie.resultTitle}</Text>
      <Text style={styles.type}>{result.silhouette_type}</Text>
      <Text style={styles.body}>{result.description}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.textMuted },
  type: { ...typography.title, color: colors.text },
  body: { ...typography.body, color: colors.text },
});
