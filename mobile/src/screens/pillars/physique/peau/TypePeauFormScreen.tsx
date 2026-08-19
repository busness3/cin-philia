import { useState } from "react";
import { Alert, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../../../content/microcopy";
import type { ProblematiquePeau, RessentiPeau, VisuelPeau } from "../../../../services/api";
import { submitTypePeau } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "TypePeauForm">;

function OptionRow<T extends string>({
  options,
  selected,
  onSelect,
}: {
  options: Record<T, string>;
  selected: T | null;
  onSelect: (value: T) => void;
}) {
  return (
    <View style={styles.optionsWrapper}>
      {(Object.keys(options) as T[]).map((key) => (
        <Pressable
          key={key}
          style={[styles.option, selected === key && styles.optionSelected]}
          onPress={() => onSelect(key)}
        >
          <Text style={[styles.optionText, selected === key && styles.optionTextSelected]}>
            {options[key]}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

export function TypePeauFormScreen({ navigation }: Props) {
  const [ressenti, setRessenti] = useState<RessentiPeau | null>(null);
  const [visuel, setVisuel] = useState<VisuelPeau | null>(null);
  const [problematique, setProblematique] = useState<ProblematiquePeau | null>(null);
  const [loading, setLoading] = useState(false);
  const { userId, setTypePeau } = useDiagnosticStore();

  const canSubmit = ressenti !== null && visuel !== null && problematique !== null && !loading;

  async function handleSubmit() {
    if (!ressenti || !visuel || !problematique) return;
    setLoading(true);
    try {
      const result = await submitTypePeau(userId, { ressenti, visuel, problematique });
      setTypePeau(result);
      navigation.navigate("TypePeauResult");
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
      <Text style={styles.title}>{microcopy.peau.intro}</Text>

      <Text style={styles.stepTitle}>{microcopy.peau.stepRessentiTitle}</Text>
      <OptionRow options={microcopy.peau.ressenti} selected={ressenti} onSelect={setRessenti} />

      {ressenti ? (
        <>
          <Text style={styles.stepTitle}>{microcopy.peau.stepVisuelTitle}</Text>
          <OptionRow options={microcopy.peau.visuel} selected={visuel} onSelect={setVisuel} />
        </>
      ) : null}

      {ressenti && visuel ? (
        <>
          <Text style={styles.stepTitle}>{microcopy.peau.stepProblematiqueTitle}</Text>
          <OptionRow
            options={microcopy.peau.problematique}
            selected={problematique}
            onSelect={setProblematique}
          />
        </>
      ) : null}

      <Pressable
        style={[styles.cta, !canSubmit && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!canSubmit}
      >
        <Text style={styles.ctaText}>{loading ? "Analyse en cours…" : microcopy.peau.cta}</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.text, marginBottom: spacing.sm },
  stepTitle: { ...typography.body, color: colors.text, marginTop: spacing.md, marginBottom: spacing.xs },
  optionsWrapper: { gap: spacing.xs },
  option: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    backgroundColor: colors.surface,
    padding: spacing.md,
  },
  optionSelected: { backgroundColor: colors.primary, borderColor: colors.primary },
  optionText: { ...typography.body, color: colors.text },
  optionTextSelected: { color: colors.surface },
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
