import { useState } from "react";
import { Alert, Image, Pressable, StyleSheet, Text, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { microcopy } from "../../../../content/microcopy";
import { submitColorimetriePhoto } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "ColorimetriePhoto">;

/**
 * Note confidentialité : même principe que la capture silhouette — la
 * photo de visage n'est jamais copiée dans un stockage applicatif, lue
 * une seule fois pour l'upload (voir services/api.ts). Voir aussi
 * backend/app/domain/physique/colorimetrie/photo_classification.py pour
 * la façon dont le backend traite (et ne conserve jamais) cette photo.
 */
export function ColorimetriePhotoScreen({ navigation }: Props) {
  const [photo, setPhoto] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const { userId, setColorimetrie } = useDiagnosticStore();

  async function pickPhoto() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Permission requise", "Autorise l'accès aux photos pour continuer.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });
    if (!result.canceled && result.assets.length > 0) {
      setPhoto(result.assets[0]);
    }
  }

  async function handleSubmit() {
    if (!photo) return;
    setLoading(true);
    try {
      const result = await submitColorimetriePhoto(userId, {
        uri: photo.uri,
        name: photo.fileName ?? "photo.jpg",
        type: photo.mimeType ?? "image/jpeg",
      });
      setColorimetrie(result);
      navigation.navigate("ColorimetrieResult");
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
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.colorimetrie.photoIntro}</Text>
      <Text style={styles.guidance}>{microcopy.colorimetrie.photoGuidance}</Text>

      <Pressable style={styles.photoPicker} onPress={pickPhoto}>
        {photo ? (
          <Image source={{ uri: photo.uri }} style={styles.photoPreview} />
        ) : (
          <Text style={styles.photoPlaceholder}>Choisir une photo</Text>
        )}
      </Pressable>

      <Pressable
        style={[styles.cta, (!photo || loading) && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!photo || loading}
      >
        <Text style={styles.ctaText}>{loading ? "Analyse en cours…" : microcopy.colorimetrie.photoCta}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.text, marginBottom: spacing.xs },
  guidance: { ...typography.caption, color: colors.textMuted, marginBottom: spacing.md },
  photoPicker: {
    height: 260,
    borderRadius: radii.lg,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  photoPreview: { width: "100%", height: "100%" },
  photoPlaceholder: { ...typography.body, color: colors.textMuted },
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
