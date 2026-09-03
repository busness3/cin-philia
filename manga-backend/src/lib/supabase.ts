import { createClient } from "@supabase/supabase-js";
import { env } from "../config/env.js";

/**
 * Client Supabase côté serveur, avec la clé service_role : contourne les
 * policies RLS. Utilisé uniquement par le job cron pour lire l'ensemble
 * des bibliothèques (tous utilisateurs confondus) et écrire les nouveaux
 * chapitres détectés / mettre à jour le cache manga_titles.
 *
 * Ne jamais exposer cette clé côté mobile : l'app mobile utilise sa
 * propre clé "anon" + l'authentification Supabase, avec RLS actif.
 */
export const supabaseAdmin = createClient(env.supabaseUrl, env.supabaseServiceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
});
