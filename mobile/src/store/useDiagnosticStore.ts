import { create } from "zustand";

import type { ColorimetrieResult, MorphologieResult } from "../services/api";

/**
 * État en mémoire uniquement pour ce prototype — aucune persistance disque
 * (AsyncStorage) pour l'instant. À évaluer plus tard : les résultats
 * (saison, type de silhouette) ne sont pas des données sensibles au même
 * titre qu'une photo, mais toute persistance locale future doit rester
 * cohérente avec le principe "les données ne quittent jamais l'app".
 */
interface DiagnosticState {
  userId: string;
  colorimetrie: ColorimetrieResult | null;
  morphologie: MorphologieResult | null;
  setColorimetrie: (result: ColorimetrieResult) => void;
  setMorphologie: (result: MorphologieResult) => void;
}

export const useDiagnosticStore = create<DiagnosticState>((set) => ({
  // Placeholder — à remplacer par le vrai user_id une fois l'auth branchée.
  userId: "prototype-user",
  colorimetrie: null,
  morphologie: null,
  setColorimetrie: (result) => set({ colorimetrie: result }),
  setMorphologie: (result) => set({ morphologie: result }),
}));
