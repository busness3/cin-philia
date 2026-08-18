import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import type * as ImagePicker from "expo-image-picker";

import { colors, radii, spacing, typography } from "../theme/tokens";

interface Props {
  label: string;
  photo: ImagePicker.ImagePickerAsset | null;
  onPress: () => void;
}

/** Vignette de sélection de photo, réutilisée partout où l'app demande une
 * photo (silhouette face/profil, colorimétrie photo 1/2). Centralise le
 * style + le fallback "Choisir une photo" en un seul endroit. */
export function PhotoPickerTile({ label, photo, onPress }: Props) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <Pressable style={styles.picker} onPress={onPress}>
        {photo ? (
          <Image source={{ uri: photo.uri }} style={styles.preview} />
        ) : (
          <Text style={styles.placeholder}>Choisir une photo</Text>
        )}
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: spacing.xs },
  label: { ...typography.body, color: colors.text },
  picker: {
    height: 200,
    borderRadius: radii.lg,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  preview: { width: "100%", height: "100%" },
  placeholder: { ...typography.body, color: colors.textMuted },
});
