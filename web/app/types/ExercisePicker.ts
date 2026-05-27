/**
 * Props du composant ExercisePicker.
 */
export interface ExercisePickerProps {
  /** Contrôle l'ouverture du panneau (v-model:open). */
  open: boolean
  /** Identifiants des exercices déjà présents dans le jour (pour les marquer comme ajoutés). */
  existingExerciseIds?: number[]
}
