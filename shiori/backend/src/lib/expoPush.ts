const EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send";
const CHUNK_SIZE = 100; // limite recommandée par l'API Expo Push

export interface PushMessage {
  to: string;
  title: string;
  body: string;
  data?: Record<string, unknown>;
}

function isExpoPushToken(token: string): boolean {
  return token.startsWith("ExponentPushToken[") || token.startsWith("ExpoPushToken[");
}

function chunk<T>(items: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size));
  }
  return chunks;
}

/**
 * Envoie des notifications push via l'API Expo Push. Volontairement
 * simple (pas de gestion des reçus de livraison / tickets d'erreur
 * détaillée) : suffisant pour un job horaire à faible volume. Les
 * jetons mal formés sont filtrés en amont pour ne pas faire échouer
 * tout le lot.
 */
export async function sendExpoPushNotifications(messages: PushMessage[]): Promise<void> {
  const valid = messages.filter((m) => isExpoPushToken(m.to));
  if (valid.length === 0) return;

  for (const batch of chunk(valid, CHUNK_SIZE)) {
    try {
      const res = await fetch(EXPO_PUSH_URL, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(batch),
      });
      if (!res.ok) {
        console.error(`Expo Push → ${res.status} ${res.statusText}`);
      }
    } catch (err) {
      console.error("Envoi Expo Push échoué pour un lot", err);
    }
  }
}
