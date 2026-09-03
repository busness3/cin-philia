import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";
import { Platform } from "react-native";
import { supabase } from "./supabase";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

/**
 * Demande la permission de notification, récupère le jeton Expo Push et
 * l'enregistre pour l'utilisateur connecté (upsert : un utilisateur peut
 * avoir plusieurs appareils). Ne fait rien sur simulateur/émulateur —
 * les push nécessitent un appareil physique.
 */
export async function registerPushToken(userId: string): Promise<void> {
  if (!Device.isDevice) {
    console.log("[push] simulateur/émulateur détecté, jeton push ignoré");
    return;
  }

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "Nouveaux chapitres",
      importance: Notifications.AndroidImportance.DEFAULT,
    });
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== "granted") {
    console.log("[push] permission refusée");
    return;
  }

  try {
    const projectId = Constants.expoConfig?.extra?.eas?.projectId;
    const token = await Notifications.getExpoPushTokenAsync(
      projectId ? { projectId } : undefined,
    );

    await supabase
      .from("push_tokens")
      .upsert(
        { user_id: userId, expo_push_token: token.data },
        { onConflict: "user_id,expo_push_token" },
      );
  } catch (err) {
    // En Expo Go / sans projet EAS configuré, la récupération du jeton
    // peut échouer — ce n'est pas bloquant pour le reste de l'app.
    console.warn("[push] jeton push indisponible :", err);
  }
}
