/**
 * Icônes Lucide et styles par groupe musculaire (affichage clair sur mobile).
 */
export interface MuscleGroupVisual {
  icon: string
  bgClass: string
  iconClass: string
}

export const MUSCLE_GROUP_VISUALS: Record<string, MuscleGroupVisual> = {
  pectoraux: { icon: 'lucide:heart-pulse', bgClass: 'bg-red-500/15', iconClass: 'text-red-400' },
  dos: { icon: 'lucide:shield', bgClass: 'bg-blue-500/15', iconClass: 'text-blue-400' },
  epaules: { icon: 'lucide:arrow-up-from-line', bgClass: 'bg-orange-500/15', iconClass: 'text-orange-400' },
  biceps: { icon: 'lucide:biceps-flexed', bgClass: 'bg-amber-500/15', iconClass: 'text-amber-400' },
  triceps: { icon: 'lucide:move-diagonal', bgClass: 'bg-violet-500/15', iconClass: 'text-violet-400' },
  jambes: { icon: 'lucide:footprints', bgClass: 'bg-emerald-500/15', iconClass: 'text-emerald-400' },
  'ischios-fessiers': { icon: 'lucide:activity', bgClass: 'bg-teal-500/15', iconClass: 'text-teal-400' },
  mollets: { icon: 'lucide:arrow-down', bgClass: 'bg-cyan-500/15', iconClass: 'text-cyan-400' },
  abdominaux: { icon: 'lucide:target', bgClass: 'bg-lime-500/15', iconClass: 'text-lime-400' },
}

const DEFAULT_VISUAL: MuscleGroupVisual = {
  icon: 'lucide:dumbbell',
  bgClass: 'bg-primary/15',
  iconClass: 'text-primary',
}

/**
 * Retourne l'icône et les classes visuelles d'un groupe musculaire.
 * @param slug - Slug du groupe musculaire.
 * @returns La configuration visuelle.
 */
export function muscleGroupVisual(slug: string): MuscleGroupVisual {
  return MUSCLE_GROUP_VISUALS[slug] ?? DEFAULT_VISUAL
}
