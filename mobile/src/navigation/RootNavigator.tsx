import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

import { PillarComingSoonCard } from "../components/PillarComingSoonCard";
import { microcopy } from "../content/microcopy";
import { WelcomeScreen } from "../screens/onboarding/WelcomeScreen";
import { PhysiqueHomeScreen } from "../screens/pillars/physique/PhysiqueHomeScreen";
import { NatureCheveuxFormScreen } from "../screens/pillars/physique/cheveux/NatureCheveuxFormScreen";
import { NatureCheveuxResultScreen } from "../screens/pillars/physique/cheveux/NatureCheveuxResultScreen";
import { ColorimetrieFormScreen } from "../screens/pillars/physique/colorimetrie/ColorimetrieFormScreen";
import { ColorimetriePhotoScreen } from "../screens/pillars/physique/colorimetrie/ColorimetriePhotoScreen";
import { ColorimetrieResultScreen } from "../screens/pillars/physique/colorimetrie/ColorimetrieResultScreen";
import { SilhouetteCaptureScreen } from "../screens/pillars/physique/morphologie/SilhouetteCaptureScreen";
import { SilhouetteResultScreen } from "../screens/pillars/physique/morphologie/SilhouetteResultScreen";
import { colors } from "../theme/tokens";

/**
 * Structure de navigation extensible aux 4 piliers dès la V1, même si seul
 * Physique est implémenté — voir docs/CLAUDE.md § Architecture extensible.
 * Mental / Organisation / Finances sont visibles mais mènent à un écran
 * "bientôt disponible" plutôt que d'être masqués.
 */

export type RootStackParamList = {
  Welcome: undefined;
  MainTabs: undefined;
};

export type PhysiqueStackParamList = {
  PhysiqueHome: undefined;
  ColorimetrieForm: undefined;
  ColorimetriePhoto: undefined;
  ColorimetrieResult: undefined;
  SilhouetteCapture: undefined;
  SilhouetteResult: undefined;
  NatureCheveuxForm: undefined;
  NatureCheveuxResult: undefined;
};

export type MainTabParamList = {
  Physique: undefined;
  Mental: undefined;
  Organisation: undefined;
  Finances: undefined;
};

const RootStack = createNativeStackNavigator<RootStackParamList>();
const PhysiqueStack = createNativeStackNavigator<PhysiqueStackParamList>();
const MainTabs = createBottomTabNavigator<MainTabParamList>();

function PhysiqueNavigator() {
  return (
    <PhysiqueStack.Navigator screenOptions={{ headerShown: false }}>
      <PhysiqueStack.Screen name="PhysiqueHome" component={PhysiqueHomeScreen} />
      <PhysiqueStack.Screen
        name="ColorimetrieForm"
        component={ColorimetrieFormScreen}
        options={{ headerShown: true, title: "Colorimétrie" }}
      />
      <PhysiqueStack.Screen
        name="ColorimetriePhoto"
        component={ColorimetriePhotoScreen}
        options={{ headerShown: true, title: "Colorimétrie par photo" }}
      />
      <PhysiqueStack.Screen
        name="ColorimetrieResult"
        component={ColorimetrieResultScreen}
        options={{ headerShown: true, title: microcopy.colorimetrie.resultTitle }}
      />
      <PhysiqueStack.Screen
        name="SilhouetteCapture"
        component={SilhouetteCaptureScreen}
        options={{ headerShown: true, title: "Morphologie" }}
      />
      <PhysiqueStack.Screen
        name="SilhouetteResult"
        component={SilhouetteResultScreen}
        options={{ headerShown: true, title: microcopy.morphologie.resultTitle }}
      />
      <PhysiqueStack.Screen
        name="NatureCheveuxForm"
        component={NatureCheveuxFormScreen}
        options={{ headerShown: true, title: "Nature des cheveux" }}
      />
      <PhysiqueStack.Screen
        name="NatureCheveuxResult"
        component={NatureCheveuxResultScreen}
        options={{ headerShown: true, title: microcopy.cheveux.resultTitle }}
      />
    </PhysiqueStack.Navigator>
  );
}

function MainTabNavigator() {
  return (
    <MainTabs.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primaryDark,
        tabBarInactiveTintColor: colors.textMuted,
      }}
    >
      <MainTabs.Screen name="Physique" component={PhysiqueNavigator} options={{ title: microcopy.pillars.physique }} />
      <MainTabs.Screen name="Mental" options={{ title: microcopy.pillars.mental }}>
        {() => <PillarComingSoonCard pillarName={microcopy.pillars.mental} />}
      </MainTabs.Screen>
      <MainTabs.Screen name="Organisation" options={{ title: microcopy.pillars.organisation }}>
        {() => <PillarComingSoonCard pillarName={microcopy.pillars.organisation} />}
      </MainTabs.Screen>
      <MainTabs.Screen name="Finances" options={{ title: microcopy.pillars.finances }}>
        {() => <PillarComingSoonCard pillarName={microcopy.pillars.finances} />}
      </MainTabs.Screen>
    </MainTabs.Navigator>
  );
}

export function RootNavigator() {
  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        <RootStack.Screen name="Welcome" component={WelcomeScreen} />
        <RootStack.Screen name="MainTabs" component={MainTabNavigator} />
      </RootStack.Navigator>
    </NavigationContainer>
  );
}
