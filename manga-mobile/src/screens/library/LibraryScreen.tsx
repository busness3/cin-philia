import React, { useCallback, useState } from "react";
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { useFocusEffect, useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { supabase } from "../../lib/supabase";
import { useAuth } from "../../context/AuthContext";
import { LibraryCard } from "../../components/LibraryCard";
import { SegmentedControl } from "../../components/SegmentedControl";
import { colors, spacing, typography } from "../../theme/tokens";
import type { LibraryEntry } from "../../types";
import type { MainStackParamList } from "../../navigation/RootNavigator";

type ViewMode = "list" | "grid";

export function LibraryScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();
  const { signOut } = useAuth();
  const [entries, setEntries] = useState<LibraryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("grid");

  const load = useCallback(async () => {
    const { data, error } = await supabase.from("library_entries").select("*");
    if (!error && data) {
      const sorted = [...data].sort((a, b) =>
        a.title.localeCompare(b.title, "fr", { sensitivity: "base" }),
      );
      setEntries(sorted as LibraryEntry[]);
    }
    setLoading(false);
    setRefreshing(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onRefresh = () => {
    setRefreshing(true);
    load();
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Bibliothèque</Text>
          <View style={styles.headerMetaRow}>
            <Text style={styles.count}>
              {entries.length} titre{entries.length > 1 ? "s" : ""}
            </Text>
            <Pressable onPress={signOut}>
              <Text style={styles.signOutLabel}>Se déconnecter</Text>
            </Pressable>
          </View>
        </View>
        <SegmentedControl
          value={viewMode}
          onChange={setViewMode}
          options={[
            { value: "grid", label: "Grille" },
            { value: "list", label: "Liste" },
          ]}
        />
      </View>

      {!loading && entries.length === 0 ? (
        <EmptyState onAdd={() => navigation.navigate("AddTitle")} />
      ) : (
        <FlatList
          key={viewMode}
          data={entries}
          keyExtractor={(item) => item.id}
          numColumns={viewMode === "grid" ? 2 : 1}
          columnWrapperStyle={viewMode === "grid" ? styles.gridRow : undefined}
          contentContainerStyle={styles.listContent}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          renderItem={({ item }) => (
            <LibraryCard
              entry={item}
              variant={viewMode}
              onPress={() => navigation.navigate("TitleDetail", { entryId: item.id })}
            />
          )}
        />
      )}

      <Pressable style={styles.fab} onPress={() => navigation.navigate("AddTitle")}>
        <Text style={styles.fabLabel}>＋</Text>
      </Pressable>
    </View>
  );
}

function EmptyState({ onAdd }: { onAdd: () => void }) {
  return (
    <View style={styles.empty}>
      <Text style={styles.emptyBrand}>栞</Text>
      <Text style={styles.emptyTitle}>Ta bibliothèque est vide</Text>
      <Text style={styles.emptyBody}>
        Ajoute ton premier titre en le recherchant — pas besoin de remplir toi-même l'affiche ou
        le titre.
      </Text>
      <Pressable style={styles.emptyButton} onPress={onAdd}>
        <Text style={styles.emptyButtonLabel}>Ajouter un titre</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.xxl,
    paddingBottom: spacing.md,
  },
  title: {
    ...typography.displayTitle,
  },
  headerMetaRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginTop: 2,
  },
  count: {
    ...typography.caption,
  },
  listContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxl * 2,
    gap: spacing.md,
  },
  gridRow: {
    justifyContent: "space-between",
    marginBottom: spacing.md,
  },
  fab: {
    position: "absolute",
    right: spacing.lg,
    bottom: spacing.xl,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.seal,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: colors.ink,
    shadowOpacity: 0.2,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  fabLabel: {
    color: colors.surface,
    fontSize: 26,
    fontFamily: typography.button.fontFamily,
    marginTop: -2,
  },
  signOutLabel: {
    ...typography.caption,
    textDecorationLine: "underline",
  },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.xxl,
    gap: spacing.sm,
  },
  emptyBrand: {
    fontSize: 36,
    color: colors.seal,
    marginBottom: spacing.sm,
  },
  emptyTitle: {
    ...typography.screenTitle,
  },
  emptyBody: {
    ...typography.bodyMuted,
    textAlign: "center",
  },
  emptyButton: {
    marginTop: spacing.lg,
    backgroundColor: colors.seal,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm + 2,
    borderRadius: 2,
  },
  emptyButtonLabel: {
    ...typography.button,
  },
});
