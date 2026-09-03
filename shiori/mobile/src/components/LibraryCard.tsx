import React from "react";
import { Image, Pressable, StyleSheet, Text, View } from "react-native";
import { colors, fonts, radii, spacing, typography } from "../theme/tokens";
import type { LibraryEntry } from "../types";
import { STATUT_LABELS, SUPPORT_LABELS } from "../types";

interface Props {
  entry: LibraryEntry;
  variant: "grid" | "list";
  onPress: () => void;
}

export function LibraryCard({ entry, variant, onPress }: Props) {
  if (variant === "grid") {
    return (
      <Pressable onPress={onPress} style={styles.gridCard}>
        <View style={styles.gridCoverWrap}>
          {entry.cover_url ? (
            <Image source={{ uri: entry.cover_url }} style={styles.gridCover} />
          ) : (
            <View style={[styles.gridCover, styles.coverPlaceholder]}>
              <Text style={styles.coverPlaceholderText}>{entry.title.charAt(0)}</Text>
            </View>
          )}
          <SupportTag support={entry.support} corner />
        </View>
        <Text style={styles.gridTitle} numberOfLines={2}>
          {entry.title}
        </Text>
        <Text style={styles.gridMeta} numberOfLines={1}>
          {entry.current_chapter ? `Ch. ${entry.current_chapter}` : STATUT_LABELS[entry.status]}
        </Text>
      </Pressable>
    );
  }

  return (
    <Pressable onPress={onPress} style={styles.listCard}>
      {entry.cover_url ? (
        <Image source={{ uri: entry.cover_url }} style={styles.listCover} />
      ) : (
        <View style={[styles.listCover, styles.coverPlaceholder]}>
          <Text style={styles.coverPlaceholderText}>{entry.title.charAt(0)}</Text>
        </View>
      )}
      <View style={styles.listBody}>
        <Text style={styles.listTitle} numberOfLines={1}>
          {entry.title}
        </Text>
        <View style={styles.listMetaRow}>
          <Text style={styles.listMeta}>
            {entry.current_chapter ? `Chapitre ${entry.current_chapter}` : "Pas encore commencé"}
          </Text>
          <Text style={styles.listMetaDot}>·</Text>
          <Text style={styles.listMeta}>{STATUT_LABELS[entry.status]}</Text>
        </View>
      </View>
      <SupportTag support={entry.support} />
    </Pressable>
  );
}

function SupportTag({ support, corner }: { support: LibraryEntry["support"]; corner?: boolean }) {
  return (
    <View style={[styles.supportTag, corner && styles.supportTagCorner]}>
      <Text style={styles.supportTagText}>{SUPPORT_LABELS[support]}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  gridCard: {
    width: "47%",
  },
  gridCoverWrap: {
    position: "relative",
  },
  gridCover: {
    width: "100%",
    aspectRatio: 3 / 4.2,
    borderRadius: radii.md,
    backgroundColor: colors.backgroundAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  gridTitle: {
    ...typography.cardTitle,
    fontSize: 15,
    marginTop: spacing.sm,
  },
  gridMeta: {
    ...typography.caption,
    marginTop: 2,
  },
  listCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.md,
    padding: spacing.sm,
    gap: spacing.md,
  },
  listCover: {
    width: 52,
    height: 72,
    borderRadius: radii.sm,
    backgroundColor: colors.backgroundAlt,
  },
  listBody: {
    flex: 1,
  },
  listTitle: {
    ...typography.cardTitle,
  },
  listMetaRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 4,
    gap: 6,
  },
  listMeta: {
    ...typography.caption,
  },
  listMetaDot: {
    ...typography.caption,
  },
  coverPlaceholder: {
    alignItems: "center",
    justifyContent: "center",
  },
  coverPlaceholderText: {
    ...typography.displayTitle,
    fontSize: 24,
    color: colors.inkFaint,
  },
  supportTag: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radii.pill,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
  },
  supportTagCorner: {
    position: "absolute",
    top: 6,
    right: 6,
    backgroundColor: colors.surface,
  },
  supportTagText: {
    fontFamily: fonts.sansMedium,
    fontSize: 10,
    color: colors.inkMuted,
  },
});
