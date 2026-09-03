function requiredEnv(name: string, value: string | undefined): string {
  if (!value) {
    console.warn(
      `[config] ${name} n'est pas défini — copie .env.example en .env.local et renseigne tes clés Supabase.`,
    );
    return "";
  }
  return value;
}

export const config = {
  supabaseUrl: requiredEnv("EXPO_PUBLIC_SUPABASE_URL", process.env.EXPO_PUBLIC_SUPABASE_URL),
  supabaseAnonKey: requiredEnv(
    "EXPO_PUBLIC_SUPABASE_ANON_KEY",
    process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
  ),
  apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:3000",
};
