import React from "react";
import { DefaultTheme, NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text } from "react-native";
import { useAuth } from "../context/AuthContext";
import { colors, fonts } from "../theme/tokens";
import { LoginScreen } from "../screens/auth/LoginScreen";
import { SignUpScreen } from "../screens/auth/SignUpScreen";
import { LibraryScreen } from "../screens/library/LibraryScreen";
import { AddTitleScreen } from "../screens/library/AddTitleScreen";
import { TitleDetailScreen } from "../screens/library/TitleDetailScreen";
import { NotificationsScreen } from "../screens/notifications/NotificationsScreen";

export type AuthStackParamList = {
  Login: undefined;
  SignUp: undefined;
};

export type MainTabParamList = {
  Bibliothèque: undefined;
  Notifications: undefined;
};

export type MainStackParamList = {
  Tabs: undefined;
  AddTitle: undefined;
  TitleDetail: { entryId: string };
};

const AuthStack = createNativeStackNavigator<AuthStackParamList>();
const MainStack = createNativeStackNavigator<MainStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

const navigationTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.background,
    card: colors.surface,
    text: colors.ink,
    border: colors.border,
    primary: colors.seal,
  },
};

function TabIcon({ symbol }: { symbol: string }) {
  return <Text style={{ fontSize: 18 }}>{symbol}</Text>;
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.seal,
        tabBarInactiveTintColor: colors.inkFaint,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarLabelStyle: { fontFamily: fonts.sansMedium, fontSize: 11 },
      }}
    >
      <Tab.Screen
        name="Bibliothèque"
        component={LibraryScreen}
        options={{ tabBarIcon: () => <TabIcon symbol="📚" /> }}
      />
      <Tab.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{ tabBarIcon: () => <TabIcon symbol="🔔" /> }}
      />
    </Tab.Navigator>
  );
}

function AuthNavigator() {
  return (
    <AuthStack.Navigator screenOptions={{ headerShown: false }}>
      <AuthStack.Screen name="Login" component={LoginScreen} />
      <AuthStack.Screen name="SignUp" component={SignUpScreen} />
    </AuthStack.Navigator>
  );
}

const headerOptions = {
  headerStyle: { backgroundColor: colors.background },
  headerTintColor: colors.ink,
  headerTitleStyle: { fontFamily: fonts.serifSemiBold, fontSize: 18 },
  headerShadowVisible: false,
} as const;

function MainNavigator() {
  return (
    <MainStack.Navigator>
      <MainStack.Screen name="Tabs" component={MainTabs} options={{ headerShown: false }} />
      <MainStack.Screen
        name="AddTitle"
        component={AddTitleScreen}
        options={{ ...headerOptions, title: "Ajouter un titre" }}
      />
      <MainStack.Screen
        name="TitleDetail"
        component={TitleDetailScreen}
        options={{ ...headerOptions, title: "Fiche" }}
      />
    </MainStack.Navigator>
  );
}

export function RootNavigator() {
  const { session, loading } = useAuth();

  if (loading) return null;

  return (
    <NavigationContainer theme={navigationTheme}>
      {session ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
