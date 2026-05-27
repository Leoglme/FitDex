import type { Exercise, ExerciseInput, MuscleGroup } from '~/types/api'

/**
 * Accès au catalogue partagé (groupes musculaires + exercices).
 *
 * Les appels passent directement par `apiFetch` (et non `useAsyncData`) afin de pouvoir
 * être déclenchés depuis des gestionnaires d'événements (sélection de catégorie) sans
 * sortir du contexte Nuxt.
 * @returns Les helpers de récupération et gestion du catalogue.
 */
export function useCatalog(): {
  fetchMuscleGroups: () => Promise<MuscleGroup[]>
  fetchExercises: (muscleGroupId: number | null, query?: string) => Promise<Exercise[]>
  createExercise: (input: ExerciseInput) => Promise<Exercise>
  updateExercise: (id: number, input: Partial<ExerciseInput>) => Promise<Exercise>
} {
  const { apiFetch } = useApi()

  /**
   * Récupère les groupes musculaires triés.
   * @returns La liste des groupes musculaires.
   */
  async function fetchMuscleGroups(): Promise<MuscleGroup[]> {
    return apiFetch<MuscleGroup[]>('/catalog/muscle-groups')
  }

  /**
   * Récupère les exercices, filtrés par groupe musculaire et/ou recherche texte.
   * @param muscleGroupId - Identifiant du groupe musculaire, ou `null` pour tout le catalogue.
   * @param query - Terme de recherche sur le nom (facultatif).
   * @returns La liste des exercices correspondants.
   */
  async function fetchExercises(muscleGroupId: number | null, query?: string): Promise<Exercise[]> {
    const params: Record<string, number | string> = {}
    if (muscleGroupId !== null) {
      params.muscle_group_id = muscleGroupId
    }
    const trimmed = query?.trim()
    if (trimmed) {
      params.q = trimmed
    }
    return apiFetch<Exercise[]>('/catalog/exercises', { query: params })
  }

  /**
   * Crée un exercice personnalisé.
   * @param input - Données de l'exercice.
   * @returns L'exercice créé.
   */
  async function createExercise(input: ExerciseInput): Promise<Exercise> {
    return apiFetch<Exercise>('/catalog/exercises', {
      method: 'POST',
      body: input,
    })
  }

  /**
   * Met à jour un exercice personnalisé.
   * @param id - Identifiant de l'exercice.
   * @param input - Champs à modifier.
   * @returns L'exercice mis à jour.
   */
  async function updateExercise(id: number, input: Partial<ExerciseInput>): Promise<Exercise> {
    return apiFetch<Exercise>(`/catalog/exercises/${id}`, {
      method: 'PATCH',
      body: input,
    })
  }

  return { fetchMuscleGroups, fetchExercises, createExercise, updateExercise }
}
