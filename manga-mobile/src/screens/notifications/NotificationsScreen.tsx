import React, { useCallback, useState } from "react";
import { FlatList, Image, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { useFocusEffect, useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { supabase } from "../../lib/supabase";
import { colors, radii, spacing, typography } from "../../theme/tokens";
import type { AppNotification } from "../../types";
import type { MainStackParamList } from "../../navigation/RootNavigator";

export function NotificationsScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<MainStackParamList>>();
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const { data, error } = await supabase
      .from("notifications")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100);
    if (!error && data) setNotifications(data as AppNotification[]);
    setLoading(false);
    setRefreshing(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const onOpen = async (notification: AppNotification) => {
    if (!notification.read) {
      setNotifications((prev) =>
        prev.map((n) => (n.id === notification.id ? { ...n, read: true } : n)),
      );
      await supabase.from("notifications").update({ read: true }).eq("id", notification.id);
    }
    navigation.navigate("TitleDetail", { entryId: notification.library_entry_id });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Notifications</Text>
      <Text style={styles.subtitle}>Nouveaux chapitres pour tes titres suivis en ligne</Text>

      {!loading && notifications.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>
            Rien de nouveau pour l'instant. Les titres en support papier ne sont jamais
            surveillés.
          </Text>
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
          renderItem={({ item }) => (
            <Pressable style={styles.row} onPress={() => onOpen(item)}>
              {!item.read && <View style={styles.dot} />}
              {item.cover_snapshot ? (
                <Image source={{ uri: item.cover_snapshot }} style={styles.cover} />
              ) : (
                <View style={[styles.cover, styles.coverPlaceholder]} />
              )}
              <View style={styles.rowBody}>
                <Text style={styles.rowTitle} numberOfLines={1}>
                  {item.title_snapshot}
                </Text>
                <Text style={styles.rowMeta}>
                  {item.new_chapters_count > 1
                    ? `${item.new_chapters_count} nouveaux chapitres · jusqu'au ${item.chapter_number}`
                    : `Chapitre ${item.chapter_number} disponible`}
                </Text>
                <Text style={styles.rowDate}>
                  {new Date(item.created_at).toLocaleString("fr-FR", {
                    day: "numeric",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </Text>
              </View>
            </Pressable>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    paddingTop: spacing.xxl,
  },
  title: {
    ...typography.displayTitle,
    paddingHorizontal: spacing.lg,
  },
  subtitle: {
    ...typography.caption,
    paddingHorizontal: spacing.lg,
    marginTop: 2,
    marginBottom: spacing.lg,
  },
  list: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.xxl,
    gap: spacing.sm,
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
  dot: {
    position: "absolute",
    top: spacing.sm,
    left: spacing.sm,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.seal,
    zIndex: 1,
  },
  cover: {
    width: 44,
    height: 60,
    borderRadius: radii.sm,
    backgroundColor: colors.backgroundAlt,
  },
  coverPlaceholder: {},
  rowBody: {
    flex: 1,
    gap: 2,
  },
  rowTitle: {
    ...typography.cardTitle,
    fontSize: 15,
  },
  rowMeta: {
    ...typography.bodyMuted,
  },
  rowDate: {
    ...typography.caption,
  },
  empty: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: spacing.xxl,
  },
  emptyText: {
    ...typography.bodyMuted,
    textAlign: "center",
  },
});
