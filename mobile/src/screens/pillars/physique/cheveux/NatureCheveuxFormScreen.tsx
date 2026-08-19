import { useState } from "react";
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../../../content/microcopy";
import type { TypeTextureCheveux } from "../../../../services/api";
import { submitNatureCheveux } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "NatureCheveuxForm">;

type Famille = "1" | "2" | "3" | "4";

const FAMILLES: Famille[] = ["1", "2", "3", "4"];
const SOUS_TYPES: Record<Famille, string[]> = {
  "1": ["A", "B", "C"],
  "2": ["A", "B", "C"],
  "3": ["A", "B", "C"],
  "4": ["A", "B", "C"],
};

/** Une option sélectionnable avec un libellé et un texte d'aide — plus
 * grande et plus descriptive qu'un simple bouton pill, adaptée à des choix
 * qui demandent un peu d'auto-observation (texture, boucles...). */
function SelectableCard({
  label,
  helper,
  selected,
  onPress,
}: {
  label: string;
  helper: string;
  selected: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable style={[styles.card, selected && styles.cardSelected]} onPress={onPress}>
      <Text style={[styles.cardLabel, selected && styles.cardLabelSelected]}>{label}</Text>
      <Text style={[styles.cardHelper, selected && styles.cardHelperSelected]}>{helper}</Text>
    </Pressable>
  );
}

export function NatureCheveuxFormScreen({ navigation }: Props) {
  const [famille, setFamille] = useState<Famille | null>(null);
  const [sousType, setSousType] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { userId, setNatureCheveux } = useDiagnosticStore();

  function pickFamille(value: Famille) {
    setFamille(value);
    setSousType(null); // changer de famille réinitialise le sous-type choisi
  }

  const canSubmit = famille !== null && sousType !== null && !loading;

  async function handleSubmit() {
    if (!famille || !sousType) return;
    const type_texture = `${famille}${sousType}` as TypeTextureCheveux;
    setLoading(true);
    try {
      const result = await submitNatureCheveux(userId, { type_texture });
      setNatureCheveux(result);
      navigation.navigate("NatureCheveuxResult");
    } catch (error) {
      Alert.alert(
        "Diagnostic pas encore disponible",
        error instanceof Error ? error.message : "Erreur inconnue.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{microcopy.cheveux.intro}</Text>

      <Text style={styles.stepTitle}>{microcopy.cheveux.stepFamilleTitle}</Text>
      {FAMILLES.map((f) => (
        <SelectableCard
          key={f}
          label={microcopy.cheveux.familles[f].label}
          helper={microcopy.cheveux.familles[f].helper}
          selected={famille === f}
          onPress={() => pickFamille(f)}
        />
      ))}

      {famille ? (
        <>
          <Text style={styles.stepTitle}>{microcopy.cheveux.stepSousTypeTitle}</Text>
          {SOUS_TYPES[famille].map((s) => {
            const type_texture = `${famille}${s}` as TypeTextureCheveux;
            return (
              <SelectableCard
                key={s}
                label={type_texture}
                helper={microcopy.cheveux.sousTypes[type_texture]}
                selected={sousType === s}
                onPress={() => setSousType(s)}
              />
            );
          })}
        </>
      ) : null}

      <Pressable
        style={[styles.cta, !canSubmit && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!canSubmit}
      >
        <Text style={styles.ctaText}>{loading ? "Analyse en cours…" : microcopy.cheveux.cta}</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.text, marginBottom: spacing.sm },
  stepTitle: { ...typography.body, color: colors.text, marginTop: spacing.md, marginBottom: spacing.xs },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs / 2,
    marginBottom: spacing.xs,
  },
  cardSelected: { backgroundColor: colors.primary, borderColor: colors.primary },
  cardLabel: { ...typography.body, color: colors.text, fontWeight: "600" },
  cardLabelSelected: { color: colors.surface },
  cardHelper: { ...typography.caption, color: colors.textMuted },
  cardHelperSelected: { color: colors.surface },
  cta: {
    marginTop: spacing.lg,
    backgroundColor: colors.primary,
    borderRadius: radii.pill,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  ctaDisabled: { opacity: 0.5 },
  ctaText: { ...typography.subtitle, color: colors.surface },
});
