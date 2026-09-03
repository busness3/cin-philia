import "react-native-url-polyfill/auto";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { createClient } from "@supabase/supabase-js";
import { config } from "./config";

/**
 * Client Supabase côté mobile — clé "anon" uniquement, toutes les
 * lectures/écritures passent par les policies RLS définies dans
 * shiori/backend/supabase/schema.sql (chaque utilisateur ne voit et ne
 * modifie que ses propres lignes).
 */
export const supabase = createClient(config.supabaseUrl, config.supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
