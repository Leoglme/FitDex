/**
 * Profil utilisateur public renvoyé par l'API.
 */
export interface UserPublic {
  id: number
  email: string
  display_name: string
  is_admin: boolean
}

/**
 * Réponse d'authentification (inscription / connexion).
 */
export interface TokenResponse {
  access_token: string
  token_type: string
}

/**
 * Type de matériel d'un exercice.
 */
export type Equipment = 'machine' | 'barbell' | 'dumbbell' | 'cable' | 'bodyweight' | 'other'

/**
 * Groupe musculaire (catégorie d'exercices).
 */
export interface MuscleGroup {
  id: number
  slug: string
  name_fr: string
  icon: string | null
  sort_order: number
}

/**
 * Exercice du catalogue.
 */
export interface Exercise {
  id: number
  slug: string
  name_fr: string
  muscle_group_id: number
  equipment: Equipment
  image_path: string | null
  description: string | null
  is_custom: boolean
}

/**
 * Données pour créer ou modifier un exercice personnalisé.
 */
export interface ExerciseInput {
  name_fr: string
  muscle_group_id: number
  equipment: Equipment
  description?: string | null
}

/**
 * Exercice rattaché à un jour de séance.
 */
export interface DayExercise {
  id: number
  position: number
  exercise: Exercise
}

/**
 * Jour de séance configuré par l'utilisateur.
 */
export interface WorkoutDay {
  id: number
  name: string
  position: number
  day_exercises: DayExercise[]
}

/**
 * Une série saisie (reps + charge).
 */
export interface SetEntry {
  set_number: number
  reps: number
  weight_kg: number
}

/**
 * Une série enregistrée (renvoyée par l'API).
 */
export interface SetLog {
  id: number
  exercise_id: number
  set_number: number
  reps: number
  weight_kg: number
}

/**
 * Séance réalisée avec ses séries.
 */
export interface WorkoutSession {
  id: number
  workout_day_id: number | null
  performed_at: string
  set_logs: SetLog[]
}

/**
 * Point d'évolution d'un exercice pour une séance.
 */
export interface ExerciseSessionPoint {
  date: string
  top_weight_kg: number
  top_set_reps: number
  total_volume_kg: number
  estimated_1rm: number
}

/**
 * Évolution complète d'un exercice dans le temps.
 */
export interface ExerciseProgress {
  exercise_id: number
  exercise_name: string
  points: ExerciseSessionPoint[]
}

/**
 * Point de volume total agrégé sur une date.
 */
export interface VolumePoint {
  date: string
  total_volume_kg: number
  sets_count: number
}

/**
 * Une série de la dernière séance enregistrée pour un exercice.
 */
export interface LastExerciseSet {
  set_number: number
  reps: number
  weight_kg: number
}

/**
 * Dernière saisie complète d'un exercice.
 */
export interface LastExerciseLog {
  performed_at: string
  sets: LastExerciseSet[]
}
