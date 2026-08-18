import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { PhotoPickerTile } from "../../../../components/PhotoPickerTile";
import { microcopy } from "../../../../content/microcopy";
import { submitColorimetriePhoto } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "ColorimetriePhoto">;

/**
 * Note confidentialité : même principe que la capture silhouette — les
 * photos de visage ne sont jamais copiées dans un stockage applicatif,
 * lues une seule fois pour l'upload (voir services/api.ts). Voir aussi
 * backend/app/domain/physique/colorimetrie/photo_classification.py pour
 * la façon dont le backend traite (et ne conserve jamais) ces photos.
 *
 * 2 photos : Claude croise les 2 lectures undertone/contraste — cohérentes
 * entre elles → confiance forte, divergentes (souvent un signe de lumière
 * trompeuse sur l'une des deux) → confiance faible, explicité à l'écran.
 */
export function ColorimetriePhotoScreen({ navigation }: Props) {
  const [photo1, setPhoto1] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [photo2, setPhoto2] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const { userId, setColorimetrie } = useDiagnosticStore();

  async function pickPhoto(onPicked: (asset: ImagePicker.ImagePickerAsset) => void) {
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
      onPicked(result.assets[0]);
    }
  }

  async function handleSubmit() {
    if (!photo1 || !photo2) return;
    setLoading(true);
    try {
      const result = await submitColorimetriePhoto(
        userId,
        { uri: photo1.uri, name: photo1.fileName ?? "photo1.jpg", type: photo1.mimeType ?? "image/jpeg" },
        { uri: photo2.uri, name: photo2.fileName ?? "photo2.jpg", type: photo2.mimeType ?? "image/jpeg" },
      );
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

  const canSubmit = photo1 !== null && photo2 !== null && !loading;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.colorimetrie.photoIntro}</Text>
      <Text style={styles.guidance}>{microcopy.colorimetrie.photoGuidance}</Text>

      <PhotoPickerTile label="Photo 1" photo={photo1} onPress={() => pickPhoto(setPhoto1)} />
      <PhotoPickerTile label="Photo 2" photo={photo2} onPress={() => pickPhoto(setPhoto2)} />

      <Pressable
        style={[styles.cta, !canSubmit && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!canSubmit}
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
