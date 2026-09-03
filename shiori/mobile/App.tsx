import React, { useEffect } from "react";
import { View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { useFonts as useShipporiMincho, ShipporiMincho_400Regular, ShipporiMincho_600SemiBold, ShipporiMincho_700Bold } from "@expo-google-fonts/shippori-mincho";
import { useFonts as useIbmPlexSans, IBMPlexSans_400Regular, IBMPlexSans_500Medium, IBMPlexSans_600SemiBold } from "@expo-google-fonts/ibm-plex-sans";
import { AuthProvider, useAuth } from "./src/context/AuthContext";
import { RootNavigator } from "./src/navigation/RootNavigator";
import { registerPushToken } from "./src/lib/notifications";
import { colors } from "./src/theme/tokens";

function PushRegistration() {
  const { session } = useAuth();

  useEffect(() => {
    if (session?.user.id) {
      registerPushToken(session.user.id);
    }
  }, [session?.user.id]);

  return null;
}

export default function App() {
  const [serifLoaded] = useShipporiMincho({
    ShipporiMincho_400Regular,
    ShipporiMincho_600SemiBold,
    ShipporiMincho_700Bold,
  });
  const [sansLoaded] = useIbmPlexSans({
    IBMPlexSans_400Regular,
    IBMPlexSans_500Medium,
    IBMPlexSans_600SemiBold,
  });

  if (!serifLoaded || !sansLoaded) {
    return <View style={{ flex: 1, backgroundColor: colors.background }} />;
  }

  return (
    <AuthProvider>
      <StatusBar style="dark" />
      <PushRegistration />
      <RootNavigator />
    </AuthProvider>
  );
}
