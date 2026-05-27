import type { Exercise } from '~/types/api'

/**
 * Props du composant TunnelLogger.
 */
export interface TunnelLoggerProps {
  /** Contrôle l'ouverture du tunnel (v-model:open). */
  open: boolean
  /** Exercice en cours de saisie (null tant qu'aucun n'est sélectionné). */
  exercise?: Exercise | null
  /** Jour de séance source (rattachement de la séance créée). */
  workoutDayId: number
  /** Séance en cours pour rattacher les exercices suivants (null = créer une nouvelle séance). */
  sessionId?: number | null
}
