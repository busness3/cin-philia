import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useFocusEffect, useNavigation, useRoute } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { RouteProp } from "@react-navigation/native";
import { supabase } from "../../lib/supabase";
import { fetchMangaDetail } from "../../lib/api";
import { Button } from "../../components/Button";
import { TextField } from "../../components/TextField";
import { colors, fonts, radii, spacing, typography } from "../../theme/tokens";
import {
  STATUT_LABELS,
  SUPPORT_LABELS,
  type ChapterSummary,
  type LibraryEntry,
  type Statut,
  type Support,
} from "../../types";
import type { MainStackParamList } from "../../navigation/RootNavigator";

type DetailRoute = RouteProp<MainStackParamList, "TitleDetail">;

const STATUTS: Statut[] = ["a_lire", "en_cours", "a_jour", "en_pause", "termine", "abandonne"];
const SUPPORTS: Support[] = ["en_ligne", "papier"];

export function TitleDetailScreen() {
  const route = useRoute<DetailRoute>();
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();
  const { entryId } = route.params;

  const [entry, setEntry] = useState<LibraryEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [recentChapters, setRecentChapters] = useState<ChapterSummary[] | null>(null);

  const [currentChapter, setCurrentChapter] = useState("");
  const [readingUrl, setReadingUrl] = useState("");
  const [support, setSupport] = useState<Support>("en_ligne");
  const [status, setStatus] = useState<Statut>("a_lire");
  const [notes, setNotes] = useState("");

  const load = useCallback(async () => {
    const { data, error } = await supabase
      .from("library_entries")
      .select("*")
      .eq("id", entryId)
      .single();
    if (!error && data) {
      const e = data as LibraryEntry;
      setEntry(e);
      setCurrentChapter(e.current_chapter ?? "");
      setReadingUrl(e.reading_url ?? "");
      setSupport(e.support);
      setStatus(e.status);
      setNotes(e.notes ?? "");
      if (e.manga_id) {
        fetchMangaDetail(e.manga_id)
          .then((detail) => setRecentChapters(detail.recentChapters.slice(0, 5)))
          .catch(() => setRecentChapters(null));
      }
    }
    setLoading(false);
  }, [entryId]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onSave = async () => {
    if (!entry) return;
    setSaving(true);
    const { error } = await supabase
      .from("library_entries")
      .update({
        current_chapter: currentChapter.trim() || null,
        reading_url: readingUrl.trim() || null,
        support,
        status,
        notes: notes.trim() || null,
      })
      .eq("id", entry.id);
    setSaving(false);
    if (error) {
      Alert.alert("Erreur", "Impossible d'enregistrer les modifications.");
      return;
    }
    navigation.goBack();
  };

  const onDelete = () => {
    if (!entry) return;
    Alert.alert("Supprimer ce titre ?", `« ${entry.title} » sera retiré de ta bibliothèque.`, [
      { text: "Annuler", style: "cancel" },
      {
        text: "Supprimer",
        style: "destructive",
        onPress: async () => {
          await supabase.from("library_entries").delete().eq("id", entry.id);
          navigation.goBack();
        },
      },
    ]);
  };

  if (loading || !entry) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.seal} />
      </View>
    );
  }

  const showsUntrackableWarning = support === "en_ligne" && !entry.manga_id;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.heroRow}>
        {entry.cover_url ? (
          <Image source={{ uri: entry.cover_url }} style={styles.cover} />
        ) : (
          <View style={[styles.cover, styles.coverPlaceholder]}>
            <Text style={styles.coverPlaceholderText}>{entry.title.charAt(0)}</Text>
          </View>
        )}
        <View style={styles.heroBody}>
          <Text style={styles.title}>{entry.title}</Text>
          <Text style={styles.source}>
            {entry.source === "mangadex"
              ? "Métadonnées MangaDex"
              : entry.source === "anilist"
                ? "Métadonnées AniList"
                : "Ajouté manuellement"}
          </Text>
        </View>
      </View>

      {showsUntrackableWarning && (
        <View style={styles.warningBox}>
          <Text style={styles.warningText}>
            Ce titre n'est pas identifié sur MangaDex : les nouveaux chapitres ne peuvent pas être
            détectés automatiquement pour lui. Tu peux toujours suivre ta lecture manuellement.
          </Text>
        </View>
      )}

      {support === "papier" && (
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            Support papier — aucune notification n'est envoyée pour ce titre (pas de source en
            ligne à surveiller).
          </Text>
        </View>
      )}

      <Field label="Chapitre en cours">
        <TextField
          label=""
          placeholder="Ex. 142"
          value={currentChapter}
          onChangeText={setCurrentChapter}
          keyboardType="default"
        />
      </Field>

      <Field label="Lien de lecture personnel">
        <TextField
          label=""
          placeholder="https://..."
          value={readingUrl}
          onChangeText={setReadingUrl}
          autoCapitalize="none"
          keyboardType="url"
        />
        {entry.reading_url ? (
          <Pressable onPress={() => Linking.openURL(entry.reading_url!)}>
            <Text style={styles.link}>Ouvrir le lien actuel ↗</Text>
          </Pressable>
        ) : null}
      </Field>

      <Field label="Support">
        <ChipGroup
          value={support}
          onChange={setSupport}
          options={SUPPORTS.map((s) => ({ value: s, label: SUPPORT_LABELS[s] }))}
        />
      </Field>

      <Field label="Statut">
        <ChipGroup
          value={status}
          onChange={setStatus}
          options={STATUTS.map((s) => ({ value: s, label: STATUT_LABELS[s] }))}
        />
      </Field>

      <Field label="Notes">
        <TextField
          label=""
          placeholder="Impressions, scan à éviter, tome acheté..."
          value={notes}
          onChangeText={setNotes}
          multiline
          numberOfLines={4}
          style={{ minHeight: 90, textAlignVertical: "top" }}
        />
      </Field>

      {recentChapters && recentChapters.length > 0 && (
        <Field label="Derniers chapitres sur MangaDex">
          {recentChapters.map((c) => (
            <Text key={c.id} style={styles.chapterLine}>
              Chapitre {c.chapter ?? "?"} · {new Date(c.publishAt).toLocaleDateString("fr-FR")}
            </Text>
          ))}
        </Field>
      )}

      <Button label="Enregistrer" onPress={onSave} loading={saving} style={{ marginTop: spacing.lg }} />
      <Button label="Supprimer ce titre" variant="ghost" onPress={onDelete} />
    </ScrollView>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={styles.field}>
      <Text style={typography.label}>{label.toUpperCase()}</Text>
      {children}
    </View>
  );
}

function ChipGroup<T extends string>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <View style={styles.chipRow}>
      {options.map((option) => {
        const active = option.value === value;
        return (
          <Pressable
            key={option.value}
            onPress={() => onChange(option.value)}
            style={[styles.chip, active && styles.chipActive]}
          >
            <Text style={[styles.chipLabel, active && styles.chipLabelActive]}>
              {option.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.background,
  },
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xxl * 2,
    gap: spacing.lg,
  },
  heroRow: {
    flexDirection: "row",
    gap: spacing.md,
  },
  cover: {
    width: 96,
    height: 132,
    borderRadius: radii.md,
    backgroundColor: colors.backgroundAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  coverPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  coverPlaceholderText: {
    ...typography.displayTitle,
    color: colors.inkFaint,
  },
  heroBody: {
    flex: 1,
    justifyContent: "center",
    gap: spacing.xs,
  },
  title: {
    ...typography.screenTitle,
  },
  source: {
    ...typography.caption,
  },
  warningBox: {
    borderWidth: 1,
    borderColor: colors.warning,
    borderRadius: radii.md,
    padding: spacing.md,
    backgroundColor: colors.surface,
  },
  warningText: {
    ...typography.bodyMuted,
    color: colors.warning,
  },
  infoBox: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    padding: spacing.md,
    backgroundColor: colors.surface,
  },
  infoText: {
    ...typography.bodyMuted,
  },
  field: {
    gap: spacing.sm,
  },
  link: {
    ...typography.caption,
    color: colors.seal,
    marginTop: spacing.xs,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  chip: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    backgroundColor: colors.surface,
  },
  chipActive: {
    backgroundColor: colors.ink,
    borderColor: colors.ink,
  },
  chipLabel: {
    fontFamily: fonts.sansMedium,
    fontSize: 13,
    color: colors.inkMuted,
  },
  chipLabelActive: {
    color: colors.surface,
  },
  chapterLine: {
    ...typography.bodyMuted,
  },
});
