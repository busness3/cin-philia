import { useRef, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import * as Sharing from "expo-sharing";
import { captureRef } from "react-native-view-shot";

import { microcopy } from "../content/microcopy";
import { colors, radii, spacing, typography } from "../theme/tokens";

interface Props {
  /** Ex. "Ma saison colorielle" — toujours à la 1re personne : c'est
   * l'utilisatrice qui partage SON résultat. */
  eyebrow: string;
  /** Le résultat lui-même (saison, type de texture…). */
  headline: string;
  /** Ligne descriptive courte sous le résultat (optionnelle). */
  detail?: string;
  /** Couleurs de palette à afficher ; sans palette, on affiche des formes
   * décoratives aux couleurs de la marque. */
  swatches?: string[];
}

// Format 4:5 (1080×1350) : le mieux affiché dans le fil Instagram, et
// recadré proprement en story / statut. La carte est dessinée à 1/3 de cette
// taille puis exportée à pleine résolution.
const CARD_WIDTH = 300;
const CARD_HEIGHT = 375;
const EXPORT_WIDTH = 1080;
const EXPORT_HEIGHT = 1350;
const MAX_SWATCHES = 8;

/**
 * Carte de résultat à partager — boucle virale du diagnostic.
 *
 * Confidentialité (docs/CLAUDE.md) : la carte ne contient JAMAIS de photo
 * ni d'identifiant de l'utilisatrice, seulement le résultat dérivé. Le
 * partage est toujours à son initiative (bouton explicite) ; l'image
 * générée ne vit que dans le cache temporaire le temps de la feuille de
 * partage du système.
 */
export function ShareResultCard({ eyebrow, headline, detail, swatches }: Props) {
  const cardRef = useRef<View>(null);
  const [isSharing, setIsSharing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const palette = swatches?.slice(0, MAX_SWATCHES) ?? [];

  async function handleShare() {
    setError(null);
    setIsSharing(true);
    try {
      if (!(await Sharing.isAvailableAsync())) {
        setError(microcopy.share.unavailable);
        return;
      }
      const uri = await captureRef(cardRef, {
        format: "png",
        quality: 1,
        width: EXPORT_WIDTH,
        height: EXPORT_HEIGHT,
        result: "tmpfile",
      });
      await Sharing.shareAsync(uri, {
        mimeType: "image/png",
        UTI: "public.png",
        dialogTitle: microcopy.share.dialogTitle,
      });
    } catch {
      setError(microcopy.share.error);
    } finally {
      setIsSharing(false);
    }
  }

  return (
    <View style={styles.wrapper}>
      {/* collapsable={false} : sans ça Android peut aplatir la vue et
          captureRef ne trouve plus rien à capturer. */}
      <View ref={cardRef} collapsable={false} style={styles.card}>
        <View style={[styles.blob, styles.blobTop]} />
        <View style={[styles.blob, styles.blobBottom]} />

        <Text style={styles.brand}>{microcopy.share.brand}</Text>

        <View style={styles.center}>
          <Text style={styles.eyebrow}>{eyebrow}</Text>
          <Text style={styles.headline} numberOfLines={2} adjustsFontSizeToFit>
            {headline}
          </Text>
          {detail ? (
            <Text style={styles.detail} numberOfLines={3}>
              {detail}
            </Text>
          ) : null}
          {palette.length > 0 ? (
            <View style={styles.palette}>
              {palette.map((hex) => (
                <View key={hex} style={[styles.swatch, { backgroundColor: hex }]} />
              ))}
            </View>
          ) : null}
        </View>

        <View>
          <Text style={styles.tagline}>{microcopy.share.tagline}</Text>
          <Text style={styles.cta}>{microcopy.share.invite}</Text>
        </View>
      </View>

      <Pressable
        accessibilityRole="button"
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
        onPress={handleShare}
        disabled={isSharing}
      >
        {isSharing ? (
          <ActivityIndicator color={colors.surface} />
        ) : (
          <Text style={styles.buttonLabel}>{microcopy.share.cta}</Text>
        )}
      </Pressable>
      <Text style={styles.privacy}>{microcopy.share.privacyNote}</Text>
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { alignItems: "center", gap: spacing.sm, marginTop: spacing.xl },
  card: {
    width: CARD_WIDTH,
    height: CARD_HEIGHT,
    borderRadius: radii.lg,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    justifyContent: "space-between",
    overflow: "hidden",
  },
  // Formes organiques douces (direction visuelle docs/CLAUDE.md).
  blob: { position: "absolute", borderRadius: radii.pill, opacity: 0.35 },
  blobTop: { width: 220, height: 220, top: -90, right: -70, backgroundColor: colors.primary },
  blobBottom: { width: 180, height: 180, bottom: -80, left: -60, backgroundColor: colors.accent },
  brand: { ...typography.caption, color: colors.primaryDark, fontWeight: "600", letterSpacing: 2 },
  center: { gap: spacing.sm },
  eyebrow: { ...typography.body, color: colors.textMuted },
  headline: { fontSize: 40, fontWeight: "600", color: colors.text },
  detail: { ...typography.body, color: colors.text },
  palette: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginTop: spacing.sm },
  // Bordure défensive pour les couleurs très claires, comme sur l'écran
  // de résultat colorimétrie.
  swatch: { width: 40, height: 40, borderRadius: radii.pill, borderWidth: 1, borderColor: colors.border },
  tagline: { ...typography.body, color: colors.text, fontStyle: "italic" },
  cta: { ...typography.caption, color: colors.textMuted, marginTop: spacing.xs },
  button: {
    backgroundColor: colors.primaryDark,
    borderRadius: radii.pill,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    minWidth: CARD_WIDTH,
    alignItems: "center",
    marginTop: spacing.sm,
  },
  buttonPressed: { opacity: 0.85 },
  buttonLabel: { ...typography.body, color: colors.surface, fontWeight: "600" },
  privacy: { ...typography.caption, color: colors.textMuted, textAlign: "center", maxWidth: CARD_WIDTH },
  error: { ...typography.caption, color: colors.primaryDark, textAlign: "center", maxWidth: CARD_WIDTH },
});
