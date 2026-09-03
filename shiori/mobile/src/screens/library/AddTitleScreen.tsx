import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Image,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { TextField } from "../../components/TextField";
import { colors, radii, spacing, typography } from "../../theme/tokens";
import { searchTitles, fetchMangaDetail } from "../../lib/api";
import { supabase } from "../../lib/supabase";
import { useAuth } from "../../context/AuthContext";
import type { SearchResultItem } from "../../types";
import type { MainStackParamList } from "../../navigation/RootNavigator";

export function AddTitleScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();
  const { session } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [searching, setSearching] = useState(false);
  const [addingKey, setAddingKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      setError(null);
      try {
        const items = await searchTitles(query.trim());
        setResults(items);
      } catch (err) {
        setError("Recherche indisponible pour le moment. Vérifie que le backend est démarré.");
      } finally {
        setSearching(false);
      }
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const resultKey = (item: SearchResultItem) =>
    item.source === "mangadex" ? `md-${item.mangadexId}` : `al-${item.anilistId}`;

  const onSelect = async (item: SearchResultItem) => {
    if (!session) return;
    setAddingKey(resultKey(item));
    setError(null);
    try {
      let mangaId: string | null = null;

      if (item.source === "mangadex" && item.mangadexId) {
        mangaId = item.mangadexId;
        const detail = await fetchMangaDetail(item.mangadexId);
        const latest = detail.latestChapter?.chapter
          ? Number.parseFloat(detail.latestChapter.chapter)
          : null;

        // Amorce le cache partagé manga_titles avec le dernier chapitre
        // connu à l'instant T, pour que le job de suivi ne notifie pas
        // rétroactivement des chapitres déjà parus avant l'ajout.
        // ignoreDuplicates : si un autre utilisateur suit déjà ce titre,
        // on ne touche pas à sa valeur (RLS interdit de toute façon
        // l'UPDATE ici, seul le backend peut la modifier).
        await supabase.from("manga_titles").upsert(
          {
            mangadex_id: item.mangadexId,
            title: item.title,
            cover_url: item.coverUrl,
            last_known_chapter: Number.isNaN(latest as number) ? null : latest,
            last_checked_at: new Date().toISOString(),
          },
          { onConflict: "mangadex_id", ignoreDuplicates: true },
        );
      }

      const { data, error: insertError } = await supabase
        .from("library_entries")
        .insert({
          user_id: session.user.id,
          manga_id: mangaId,
          anilist_id: item.source === "anilist" ? item.anilistId : null,
          source: item.source,
          title: item.title,
          cover_url: item.coverUrl,
          support: "en_ligne",
          status: "a_lire",
        })
        .select()
        .single();

      if (insertError || !data) {
        setError("Impossible d'ajouter ce titre à ta bibliothèque.");
        return;
      }

      navigation.replace("TitleDetail", { entryId: data.id });
    } finally {
      setAddingKey(null);
    }
  };

  return (
    <View style={styles.container}>
      <TextField
        label="Rechercher un titre"
        placeholder="One Piece, Solo Leveling, Chainsaw Man..."
        value={query}
        onChangeText={setQuery}
        autoFocus
      />

      {searching && <ActivityIndicator style={{ marginTop: spacing.lg }} color={colors.seal} />}
      {error && <Text style={styles.error}>{error}</Text>}

      <FlatList
        data={results}
        keyExtractor={resultKey}
        contentContainerStyle={{ gap: spacing.sm, paddingTop: spacing.lg, paddingBottom: spacing.xxl }}
        renderItem={({ item }) => (
          <ResultRow
            item={item}
            adding={addingKey === resultKey(item)}
            onPress={() => onSelect(item)}
          />
        )}
        ListEmptyComponent={
          !searching && query.trim().length >= 2 ? (
            <Text style={styles.empty}>Aucun résultat pour « {query} ».</Text>
          ) : null
        }
      />
    </View>
  );
}

function ResultRow({
  item,
  adding,
  onPress,
}: {
  item: SearchResultItem;
  adding: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable style={styles.row} onPress={onPress} disabled={adding}>
      {item.coverUrl ? (
        <Image source={{ uri: item.coverUrl }} style={styles.cover} />
      ) : (
        <View style={[styles.cover, styles.coverPlaceholder]}>
          <Text style={styles.coverPlaceholderText}>{item.title.charAt(0)}</Text>
        </View>
      )}
      <View style={styles.rowBody}>
        <Text style={styles.rowTitle} numberOfLines={2}>
          {item.title}
        </Text>
        <View style={styles.badgeRow}>
          <Text style={styles.badge}>{item.source === "mangadex" ? "MangaDex" : "AniList"}</Text>
          {!item.trackable && (
            <Text style={[styles.badge, styles.badgeWarning]}>Pas de suivi auto</Text>
          )}
          {item.year && <Text style={styles.year}>{item.year}</Text>}
        </View>
      </View>
      {adding ? (
        <ActivityIndicator color={colors.seal} />
      ) : (
        <Text style={styles.addSymbol}>＋</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.lg,
  },
  error: {
    ...typography.bodyMuted,
    color: colors.seal,
    marginTop: spacing.md,
  },
  empty: {
    ...typography.bodyMuted,
    textAlign: "center",
    marginTop: spacing.xl,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    padding: spacing.sm,
  },
  cover: {
    width: 48,
    height: 66,
    borderRadius: radii.sm,
    backgroundColor: colors.backgroundAlt,
  },
  coverPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  coverPlaceholderText: {
    ...typography.cardTitle,
    color: colors.inkFaint,
  },
  rowBody: {
    flex: 1,
    gap: 4,
  },
  rowTitle: {
    ...typography.cardTitle,
  },
  badgeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  badge: {
    ...typography.caption,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.pill,
    paddingHorizontal: spacing.xs,
    paddingVertical: 1,
  },
  badgeWarning: {
    color: colors.warning,
    borderColor: colors.warning,
  },
  year: {
    ...typography.caption,
  },
  addSymbol: {
    fontSize: 22,
    color: colors.seal,
  },
});
