import { Pressable, StyleSheet, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../../content/microcopy";
import { colors, radii, spacing, typography } from "../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "PhysiqueHome">;

export function PhysiqueHomeScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.pillars.physique}</Text>

      <Pressable style={styles.card} onPress={() => navigation.navigate("ColorimetrieForm")}>
        <Text style={styles.cardTitle}>Colorimétrie</Text>
        <Text style={styles.cardBody}>{microcopy.colorimetrie.intro}</Text>
      </Pressable>

      <Pressable style={styles.card} onPress={() => navigation.navigate("SilhouetteCapture")}>
        <Text style={styles.cardTitle}>Morphologie</Text>
        <Text style={styles.cardBody}>{microcopy.morphologie.captureIntro}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, gap: spacing.md },
  title: { ...typography.title, color: colors.text, marginBottom: spacing.sm },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radii.lg,
    padding: spacing.lg,
    gap: spacing.xs,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cardTitle: { ...typography.subtitle, color: colors.text },
  cardBody: { ...typography.body, color: colors.textMuted },
});
