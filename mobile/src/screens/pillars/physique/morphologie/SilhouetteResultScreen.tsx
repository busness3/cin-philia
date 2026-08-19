import { ScrollView, StyleSheet, Text, View } from "react-native";

import { microcopy } from "../../../../content/microcopy";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";

/** Un trait secondaire (forme du visage, forme des yeux...) : titre de
 * section, type identifié, description et conseils associés. Factorisé
 * pour éviter de dupliquer ce bloc à chaque nouvelle catégorie ajoutée à
 * l'écran résultat morphologie. */
function TraitSection({
  sectionTitle,
  forme,
  description,
  conseils,
  conseilsTitle,
}: {
  sectionTitle: string;
  forme: string;
  description: string;
  conseils: string[];
  conseilsTitle: string;
}) {
  return (
    <View style={styles.section}>
      <Text style={styles.title}>{sectionTitle}</Text>
      <Text style={styles.type}>{forme}</Text>
      <Text style={styles.body}>{description}</Text>

      {conseils.length > 0 ? (
        <View style={styles.conseils}>
          <Text style={styles.conseilsTitle}>{conseilsTitle}</Text>
          {conseils.map((conseil) => (
            <Text key={conseil} style={styles.conseil}>
              •{"  "}
              {conseil}
            </Text>
          ))}
        </View>
      ) : null}
    </View>
  );
}

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
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{microcopy.morphologie.resultTitle}</Text>
      <Text style={styles.type}>{result.silhouette_type}</Text>
      <Text style={styles.body}>{result.description}</Text>

      {result.forme_visage ? (
        <TraitSection
          sectionTitle={microcopy.morphologie.formeVisageTitle}
          forme={result.forme_visage.forme}
          description={result.forme_visage.description}
          conseils={result.forme_visage.conseils_style}
          conseilsTitle={microcopy.morphologie.conseilsStyleTitle}
        />
      ) : (
        <Text style={styles.note}>{microcopy.morphologie.formeVisageUnavailable}</Text>
      )}

      {result.forme_yeux ? (
        <TraitSection
          sectionTitle={microcopy.morphologie.formeYeuxTitle}
          forme={result.forme_yeux.forme}
          description={result.forme_yeux.description}
          conseils={result.forme_yeux.conseils_maquillage}
          conseilsTitle={microcopy.morphologie.conseilsMaquillageTitle}
        />
      ) : (
        <Text style={styles.note}>{microcopy.morphologie.formeYeuxUnavailable}</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.textMuted },
  type: { ...typography.title, color: colors.text },
  body: { ...typography.body, color: colors.text },
  note: { ...typography.caption, color: colors.textMuted, marginTop: spacing.md },
  section: {
    marginTop: spacing.lg,
    paddingTop: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: spacing.sm,
  },
  conseils: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  conseilsTitle: { ...typography.body, color: colors.text, fontWeight: "600" },
  conseil: { ...typography.body, color: colors.textMuted },
});
