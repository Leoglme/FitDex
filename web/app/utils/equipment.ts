import type { Equipment } from '~/types/api'

/**
 * Libellés FR lisibles pour chaque type de matériel d'exercice.
 */
const EQUIPMENT_LABELS: Record<Equipment, string> = {
  machine: 'Machine',
  barbell: 'Barre',
  dumbbell: 'Haltères',
  cable: 'Poulie',
  bodyweight: 'Poids du corps',
  other: 'Autre',
}

/**
 * Icône Lucide associée à chaque type de matériel.
 */
const EQUIPMENT_ICONS: Record<Equipment, string> = {
  machine: 'lucide:cog',
  barbell: 'lucide:dumbbell',
  dumbbell: 'lucide:dumbbell',
  cable: 'lucide:cable',
  bodyweight: 'lucide:user',
  other: 'lucide:circle-dot',
}

/**
 * Retourne le libellé FR lisible d'un type de matériel.
 * @param equipment - Code matériel renvoyé par l'API.
 * @returns Le libellé affichable.
 */
export function equipmentLabel(equipment: Equipment): string {
  return EQUIPMENT_LABELS[equipment] ?? 'Autre'
}

/**
 * Retourne l'icône Lucide d'un type de matériel.
 * @param equipment - Code matériel renvoyé par l'API.
 * @returns Le nom de l'icône (préfixe lucide:).
 */
export function equipmentIcon(equipment: Equipment): string {
  return EQUIPMENT_ICONS[equipment] ?? 'lucide:circle-dot'
}
