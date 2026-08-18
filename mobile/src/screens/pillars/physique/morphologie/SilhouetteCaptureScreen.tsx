import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";

import { PhotoPickerTile } from "../../../../components/PhotoPickerTile";
import { microcopy } from "../../../../content/microcopy";
import { submitSilhouette } from "../../../../services/api";
import { useDiagnosticStore } from "../../../../store/useDiagnosticStore";
import { colors, radii, spacing, typography } from "../../../../theme/tokens";
import type { PhysiqueStackParamList } from "../../../../navigation/RootNavigator";

type Props = NativeStackScreenProps<PhysiqueStackParamList, "SilhouetteCapture">;

/**
 * Note confidentialité : `photo.uri` pointe vers le fichier temporaire créé
 * par le sélecteur d'image côté OS. On ne le copie/persiste jamais dans un
 * stockage applicatif — on le lit une seule fois pour l'upload, voir
 * services/api.ts::submitSilhouette.
 *
 * 2 photos (face + profil) : une seule photo donne ~50% de précision sur
 * la silhouette (limite documentée du produit) — la vue de profil montre
 * des volumes que la vue de face seule ne montre pas.
 */
export function SilhouetteCaptureScreen({ navigation }: Props) {
  const [photoFace, setPhotoFace] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [photoProfil, setPhotoProfil] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [mesures, setMesures] = useState("");
  const [loading, setLoading] = useState(false);
  const { userId, setMorphologie } = useDiagnosticStore();

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
    if (!photoFace || !photoProfil || mesures.trim().length === 0) return;
    setLoading(true);
    try {
      const result = await submitSilhouette(
        userId,
        mesures.trim(),
        { uri: photoFace.uri, name: photoFace.fileName ?? "face.jpg", type: photoFace.mimeType ?? "image/jpeg" },
        {
          uri: photoProfil.uri,
          name: photoProfil.fileName ?? "profil.jpg",
          type: photoProfil.mimeType ?? "image/jpeg",
        },
      );
      setMorphologie(result);
      navigation.navigate("SilhouetteResult");
    } catch (error) {
      // Le prompt de classification est encore un placeholder côté backend
      // en V1 prototype — voir backend/app/domain/physique/morphologie/
      Alert.alert(
        "Diagnostic pas encore disponible",
        error instanceof Error ? error.message : "Erreur inconnue.",
      );
    } finally {
      setLoading(false);
    }
  }

  const canSubmit = photoFace !== null && photoProfil !== null && mesures.trim().length > 0 && !loading;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{microcopy.morphologie.captureIntro}</Text>

      <PhotoPickerTile label="Vue de face" photo={photoFace} onPress={() => pickPhoto(setPhotoFace)} />
      <PhotoPickerTile label="Vue de profil" photo={photoProfil} onPress={() => pickPhoto(setPhotoProfil)} />

      <Text style={styles.label}>Mesures déclarées (tour de poitrine / taille / hanches)</Text>
      <TextInput
        style={styles.input}
        placeholder="ex : 90 / 70 / 98"
        placeholderTextColor={colors.textMuted}
        value={mesures}
        onChangeText={setMesures}
      />

      <Pressable
        style={[styles.cta, !canSubmit && styles.ctaDisabled]}
        onPress={handleSubmit}
        disabled={!canSubmit}
      >
        <Text style={styles.ctaText}>{loading ? "Analyse en cours…" : "Révéler ma silhouette"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background, padding: spacing.lg, gap: spacing.sm },
  title: { ...typography.subtitle, color: colors.text, marginBottom: spacing.sm },
  label: { ...typography.body, color: colors.text, marginTop: spacing.md },
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
