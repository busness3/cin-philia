import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../../../content/microcopy";
import type { NiveauContraste, Undertone } from "../../../../services/api";
import { submitColorimetrie } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "ColorimetrieForm">;

const UNDERTONES: Undertone[] = ["chaud", "froid", "neutre"];
const CONTRASTES: NiveauContraste[] = ["faible", "moyen", "fort"];

function ChoiceRow<T extends string>({
  options,
  selected,
  onSelect,
}: {
  options: T[];
  selected: T | null;
  onSelect: (value: T) => void;
}) {
  return (
    <View style={styles.choiceRow}>
      {options.map((option) => (
        <Pressable
          key={option}
          onPress={() => onSelect(option)}
          style={[styles.choice, selected === option && styles.choiceSelected]}
        >
          <Text style={[styles.choiceText, selected === option && styles.choiceTextSelected]}>
            {option}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

export function ColorimetrieFormScreen({ navigation }: Props) {
  const [undertone, setUndertone] = useState<Undertone | null>(null);
  const [contraste, setContraste] = useState<NiveauContraste | null>(null);
  const [couleurCheveux, setCouleurCheveux] = useState("");
  const [loading, setLoading] = useState(false);
  const { userId, setColorimetrie } = useDiagnosticStore();

  const canSubmit = undertone && contraste && couleurCheveux.trim().length > 0 && !loading;

  async function handleSubmit() {
    if (!undertone || !contraste) return;
    setLoading(true);
    try {
      const result = await submitColorimetrie(userId, {
        undertone,
        niveau_contraste: contraste,
        couleur_cheveux: couleurCheveux.trim(),
      });
      setColorimetrie(result);
      navigation.navigate("ColorimetrieResult");
    } catch (error) {
      // La table de règles est encore un placeholder côté backend en V1
      // prototype — voir backend/app/domain/physique/colorimetrie/rules.py
      Alert.alert(
        "Diagnostic pas encore disponible",
        error instanceof Error ? error.message : "Erreur inconnue.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.colorimetrie.intro}</Text>

      <Text style={styles.label}>Sous-ton de peau</Text>
      <ChoiceRow options={UNDERTONES} selected={undertone} onSelect={setUndertone} />

      <Text style={styles.label}>Niveau de contraste</Text>
      <ChoiceRow options={CONTRASTES} selected={contraste} onSelect={setContraste} />

      <Text style={styles.label}>Couleur de cheveux</Text>
      <TextInput
        style={styles.input}
        placeholder="ex : châtain foncé"
        placeholderTextColor={colors.textMuted}
        value={couleurCheveux}
        onChangeText={setCouleurCheveux}
      />

      <Pressable
        style={[styles.cta, !canSubmit && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!canSubmit}
      >
        <Text style={styles.ctaText}>{loading ? "Analyse en cours…" : "Révéler ma palette"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.text, marginBottom: spacing.sm },
  label: { ...typography.body, color: colors.text, marginTop: spacing.md },
  choiceRow: { flexDirection: "row", gap: spacing.sm },
  choice: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  choiceSelected: { backgroundColor: colors.primary, borderColor: colors.primary },
  choiceText: { ...typography.caption, color: colors.text },
  choiceTextSelected: { color: colors.surface },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    padding: spacing.md,
    color: colors.text,
    backgroundColor: colors.surface,
  },
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
