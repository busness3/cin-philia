import "dotenv/config";

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Variable d'environnement manquante : ${name} (voir .env.example)`);
  }
  return value;
}

export const env = {
  port: Number(process.env.PORT ?? 3000),
  supabaseUrl: required("SUPABASE_URL"),
  supabaseServiceRoleKey: required("SUPABASE_SERVICE_ROLE_KEY"),
  chapterCheckCron: process.env.CHAPTER_CHECK_CRON ?? "0 * * * *",
  mangadexUserAgent:
    process.env.MANGADEX_USER_AGENT ?? "cin-philia-manga-tracker/1.0",
  corsOrigin: process.env.CORS_ORIGIN ?? "*",
};
