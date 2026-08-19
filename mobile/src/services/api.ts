/**
 * Client API — appelle le backend Reveal You.
 *
 * Note confidentialité : la photo est envoyée en HTTPS directement au
 * backend (qui la transmet à Claude puis la jette — voir backend/app).
 * Elle n'est jamais écrite sur le disque de l'appareil au-delà du buffer
 * nécessaire à l'upload.
 */

// À remplacer par la vraie URL de déploiement en prod (variable d'env Expo).
const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Undertone = "chaud" | "froid" | "neutre";
export type NiveauContraste = "faible" | "moyen" | "fort";

export interface ColorimetrieInput {
  undertone: Undertone;
  niveau_contraste: NiveauContraste;
  couleur_cheveux: string;
}

export interface ColorimetrieResult {
  saison: string;
  sous_saison: string | null;
  palette: string[];
  confiance: string;
  justification: string | null;
  conseils_style: string[];
}

export interface FormeVisageResult {
  forme: string;
  confiance: string;
  description: string;
  conseils_style: string[];
}

export interface FormeYeuxResult {
  forme: string;
  confiance: string;
  description: string;
  conseils_maquillage: string[];
}

export interface SourcilsResult {
  forme: string;
  confiance: string;
  description: string;
  conseils_style: string[];
}

export interface MorphologieResult {
  silhouette_type: string;
  confiance: string;
  description: string;
  // Absents si leur classification a échoué côté backend — le résultat
  // silhouette reste affiché seul dans ce cas.
  forme_visage: FormeVisageResult | null;
  forme_yeux: FormeYeuxResult | null;
  sourcils: SourcilsResult | null;
}

// Méthode André Walker — voir microcopy.cheveux pour les libellés affichés.
// Déclaratif uniquement (pas de photo) : l'utilisatrice choisit sa famille
// (1-4) puis son sous-type (A/B/C) elle-même.
export type TypeTextureCheveux =
  | "1A"
  | "1B"
  | "1C"
  | "2A"
  | "2B"
  | "2C"
  | "3A"
  | "3B"
  | "3C"
  | "4A"
  | "4B"
  | "4C";

export interface NatureCheveuxInput {
  type_texture: TypeTextureCheveux;
}

export interface NatureCheveuxResult {
  type_texture: string;
  description: string;
  conseils_style: string[];
}

// Type de peau — voir microcopy.peau pour les libellés affichés. Déclaratif
// uniquement (pas de photo, jugée peu fiable pour cette catégorie) : 3
// questions (ressenti, visuel, préoccupation) déterminent le type.
export type RessentiPeau = "equilibree" | "tiraille" | "brille" | "variable_selon_zones" | "reactive";
export type VisuelPeau =
  | "pores_peu_visibles"
  | "zones_seches"
  | "brillance_zone_t"
  | "zone_t_grasse_joues_seches"
  | "rougeurs";
export type ProblematiquePeau =
  | "rien_de_particulier"
  | "manque_hydratation"
  | "imperfections"
  | "double_besoin"
  | "reactions_aux_produits";

export interface TypePeauInput {
  ressenti: RessentiPeau;
  visuel: VisuelPeau;
  problematique: ProblematiquePeau;
}

export interface TypePeauResult {
  type_peau: string;
  description: string;
  conseils_style: string[];
}

export interface PhotoUpload {
  uri: string;
  name: string;
  type: string;
}

async function parseOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Erreur API (${response.status}) : ${detail}`);
  }
  return response.json() as Promise<T>;
}

// `photos` associe le nom du champ multipart attendu par le backend (ex.
// "photo_face", "photo_profil") à la photo à envoyer sous ce champ.
async function postPhotos<T>(
  path: string,
  params: Record<string, string>,
  photos: Record<string, PhotoUpload>,
): Promise<T> {
  const formData = new FormData();
  // React Native FormData accepte cette forme (uri/name/type) pour un fichier.
  for (const [field, photo] of Object.entries(photos)) {
    formData.append(field, { uri: photo.uri, name: photo.name, type: photo.type } as unknown as Blob);
  }

  const response = await fetch(`${API_BASE_URL}${path}?${new URLSearchParams(params).toString()}`, {
    method: "POST",
    body: formData,
  });
  return parseOrThrow<T>(response);
}

export async function submitColorimetrie(
  userId: string,
  input: ColorimetrieInput,
): Promise<ColorimetrieResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/diagnostics/colorimetrie?user_id=${encodeURIComponent(userId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    },
  );
  return parseOrThrow<ColorimetrieResult>(response);
}

export async function submitColorimetriePhoto(
  userId: string,
  photo1: PhotoUpload,
  photo2: PhotoUpload,
): Promise<ColorimetrieResult> {
  return postPhotos<ColorimetrieResult>(
    "/api/v1/diagnostics/colorimetrie/photo",
    { user_id: userId },
    { photo_1: photo1, photo_2: photo2 },
  );
}

export async function submitSilhouette(
  userId: string,
  mesuresDeclarees: string,
  photoFace: PhotoUpload,
  photoProfil: PhotoUpload,
): Promise<MorphologieResult> {
  return postPhotos<MorphologieResult>(
    "/api/v1/diagnostics/morphologie/silhouette",
    { user_id: userId, mesures_declarees: mesuresDeclarees },
    { photo_face: photoFace, photo_profil: photoProfil },
  );
}

export async function submitNatureCheveux(
  userId: string,
  input: NatureCheveuxInput,
): Promise<NatureCheveuxResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/diagnostics/cheveux/nature?user_id=${encodeURIComponent(userId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    },
  );
  return parseOrThrow<NatureCheveuxResult>(response);
}

export async function submitTypePeau(userId: string, input: TypePeauInput): Promise<TypePeauResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/diagnostics/peau/type?user_id=${encodeURIComponent(userId)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    },
  );
  return parseOrThrow<TypePeauResult>(response);
}
