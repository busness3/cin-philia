import { Pressable, StyleSheet, Text, View } from "react-native";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../content/microcopy";
import { colors, radii, spacing, typography } from "../../theme/tokens";
import type { RootStackParamList } from "../../navigation/RootNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Welcome">;

export function WelcomeScreen({ navigation }: Props) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.onboarding.welcomeTitle}</Text>
      <Text style={styles.body}>{microcopy.onboarding.welcomeBody}</Text>
      <Pressable style={styles.cta} onPress={() => navigation.replace("MainTabs")}>
        <Text style={styles.ctaText}>{microcopy.onboarding.ctaStart}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: "center",
    padding: spacing.xl,
    gap: spacing.md,
  },
  title: { ...typography.title, color: colors.text },
  body: { ...typography.body, color: colors.textMuted },
  cta: {
    marginTop: spacing.lg,
    backgroundColor: colors.primary,
    borderRadius: radii.pill,
    paddingVertical: spacing.md,
    alignItems: "center",
  },
  ctaText: { ...typography.subtitle, color: colors.surface },
});
