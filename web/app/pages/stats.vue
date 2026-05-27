<template>
  <div class="flex flex-col gap-8">
    <div>
      <h1 class="text-2xl font-extrabold">Statistiques</h1>
      <p class="text-muted text-sm">Suis l'évolution de tes charges, reps et volume.</p>
    </div>

    <!-- Progression par exercice -->
    <section class="border-default bg-elevated/30 rounded-2xl border p-4">
      <div class="flex items-center gap-2">
        <UIcon name="lucide:trending-up" class="text-primary h-5 w-5" />
        <h2 class="font-bold">Progression par exercice</h2>
      </div>
      <p class="text-muted mt-1 text-xs">
        Le 1RM estimé combine charge et reps : il monte que tu pousses plus lourd ou que tu fasses plus de reps.
      </p>

      <USelect
        v-model="selectedExerciseId"
        :items="exerciseOptions"
        placeholder="Choisir un exercice"
        class="mt-4 w-full"
        icon="lucide:dumbbell"
      />

      <div v-if="loadingExercise" class="mt-4">
        <USkeleton class="h-60 w-full rounded-xl" />
      </div>

      <template v-else-if="selectedExerciseId && exerciseProgress">
        <div v-if="exerciseProgress.points.length > 0">
          <div class="mt-4 grid grid-cols-3 gap-2">
            <div class="bg-elevated/60 rounded-xl p-3 text-center">
              <p class="text-muted text-xs">Charge max</p>
              <p class="text-lg font-extrabold">
                {{ formatNum(latestPoint?.top_weight_kg) }}<span class="text-muted text-xs"> kg</span>
              </p>
            </div>
            <div class="bg-elevated/60 rounded-xl p-3 text-center">
              <p class="text-muted text-xs">Reps (top)</p>
              <p class="text-lg font-extrabold">{{ latestPoint?.top_set_reps ?? '–' }}</p>
            </div>
            <div class="bg-elevated/60 rounded-xl p-3 text-center">
              <p class="text-muted text-xs">1RM estimé</p>
              <p class="text-primary text-lg font-extrabold">
                {{ formatNum(latestPoint?.estimated_1rm) }}<span class="text-muted text-xs"> kg</span>
              </p>
            </div>
          </div>

          <VisBulletLegend :items="exerciseLegend" class="mt-4" />
          <VisXYContainer :data="exercisePoints" :height="240" class="unovis-xy-container mt-1">
            <VisLine :x="xAccessor" :y="[oneRmAccessor, weightAccessor]" :color="exerciseColors" />
            <VisScatter :x="xAccessor" :y="oneRmAccessor" :size="6" color="#84cc16" />
            <VisAxis type="x" :tick-format="formatDateTick" :num-ticks="4" />
            <VisAxis type="y" />
            <VisCrosshair :template="exerciseTooltip" color="#84cc16" />
            <VisTooltip />
          </VisXYContainer>
        </div>
        <p v-else class="text-muted mt-6 text-center text-sm">
          Aucune donnée pour cet exercice. Enregistre une séance pour voir ta progression.
        </p>
      </template>

      <p v-else class="text-muted mt-6 text-center text-sm">Sélectionne un exercice pour afficher sa courbe.</p>
    </section>

    <!-- Volume par muscle / type de séance -->
    <section class="border-default bg-elevated/30 rounded-2xl border p-4">
      <div class="flex items-center gap-2">
        <UIcon name="lucide:bar-chart-3" class="text-primary h-5 w-5" />
        <h2 class="font-bold">Volume dans le temps</h2>
      </div>
      <p class="text-muted mt-1 text-xs">
        Volume total soulevé (kg × reps) par jour, filtrable par muscle ou type de séance.
      </p>

      <div class="mt-4 grid grid-cols-2 gap-2">
        <USelect
          v-model="selectedMuscleId"
          :items="muscleOptions"
          placeholder="Tous les muscles"
          icon="lucide:target"
        />
        <USelect v-model="selectedDayId" :items="dayOptions" placeholder="Toutes les séances" icon="lucide:calendar" />
      </div>

      <div v-if="loadingVolume" class="mt-4">
        <USkeleton class="h-60 w-full rounded-xl" />
      </div>
      <template v-else>
        <VisXYContainer
          v-if="volumePoints.length > 0"
          :data="volumePoints"
          :height="240"
          class="unovis-xy-container mt-4"
        >
          <VisArea :x="xAccessor" :y="volumeAccessor" color="#84cc16" :opacity="0.18" />
          <VisLine :x="xAccessor" :y="volumeAccessor" color="#84cc16" />
          <VisAxis type="x" :tick-format="formatDateTick" :num-ticks="4" />
          <VisAxis type="y" />
          <VisCrosshair :template="volumeTooltip" color="#84cc16" />
          <VisTooltip />
        </VisXYContainer>
        <p v-else class="text-muted mt-6 text-center text-sm">Aucun volume enregistré pour ce filtre.</p>
      </template>
    </section>
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef, Ref } from 'vue'
import {
  VisArea,
  VisAxis,
  VisBulletLegend,
  VisCrosshair,
  VisLine,
  VisScatter,
  VisTooltip,
  VisXYContainer,
} from '@unovis/vue'
import type { ExerciseProgress, ExerciseSessionPoint, MuscleGroup, VolumePoint, WorkoutDay } from '~/types/api'

definePageMeta({ middleware: 'auth' })

/** Option de sélection (USelect). */
interface SelectOption {
  label: string
  value: number | undefined
}

const { apiFetch } = useApi()

const exerciseColors: string[] = ['#84cc16', '#10b981']
const exerciseLegend: { name: string }[] = [{ name: '1RM estimé' }, { name: 'Charge max' }]

// Données de référence (exercices configurés, muscles, jours)
const { data: workoutDays } = await useAsyncData<WorkoutDay[]>(
  'stats-workout-days',
  () => apiFetch<WorkoutDay[]>('/workout-days'),
  { default: () => [] },
)
const { data: muscleGroups } = await useAsyncData<MuscleGroup[]>(
  'stats-muscle-groups',
  () => apiFetch<MuscleGroup[]>('/catalog/muscle-groups'),
  { default: () => [] },
)

const selectedExerciseId: Ref<number | undefined> = ref(undefined)
const selectedMuscleId: Ref<number | undefined> = ref(undefined)
const selectedDayId: Ref<number | undefined> = ref(undefined)

const exerciseProgress: Ref<ExerciseProgress | null> = ref(null)
const volumePoints: Ref<VolumePoint[]> = ref([])
const loadingExercise: Ref<boolean> = ref(false)
const loadingVolume: Ref<boolean> = ref(false)

/**
 * Liste unique des exercices configurés par l'utilisateur (toutes séances confondues).
 */
const exerciseOptions: ComputedRef<SelectOption[]> = computed(() => {
  const seen: Map<number, string> = new Map()
  for (const day of workoutDays.value ?? []) {
    for (const de of day.day_exercises) {
      seen.set(de.exercise.id, de.exercise.name_fr)
    }
  }
  return [...seen.entries()].map(([value, label]: [number, string]) => ({ label, value }))
})

const muscleOptions: ComputedRef<SelectOption[]> = computed(() => [
  { label: 'Tous les muscles', value: undefined },
  ...(muscleGroups.value ?? []).map((m: MuscleGroup) => ({ label: m.name_fr, value: m.id })),
])

const dayOptions: ComputedRef<SelectOption[]> = computed(() => [
  { label: 'Toutes les séances', value: undefined },
  ...(workoutDays.value ?? []).map((d: WorkoutDay) => ({ label: d.name, value: d.id })),
])

const exercisePoints: ComputedRef<ExerciseSessionPoint[]> = computed(() => exerciseProgress.value?.points ?? [])

const latestPoint: ComputedRef<ExerciseSessionPoint | undefined> = computed(() => exercisePoints.value.at(-1))

/**
 * Accès X (timestamp) pour les graphiques temporels.
 * @param point - Point de données (exercice ou volume).
 * @returns Le timestamp en millisecondes.
 */
function xAccessor(point: ExerciseSessionPoint | VolumePoint): number {
  return new Date(point.date).getTime()
}

/**
 * Accès Y : 1RM estimé.
 * @param point - Point de progression d'exercice.
 * @returns Le 1RM estimé.
 */
function oneRmAccessor(point: ExerciseSessionPoint): number {
  return Number(point.estimated_1rm)
}

/**
 * Accès Y : charge max de la séance.
 * @param point - Point de progression d'exercice.
 * @returns La charge max (kg).
 */
function weightAccessor(point: ExerciseSessionPoint): number {
  return Number(point.top_weight_kg)
}

/**
 * Accès Y : volume total soulevé.
 * @param point - Point de volume.
 * @returns Le volume total (kg).
 */
function volumeAccessor(point: VolumePoint): number {
  return Number(point.total_volume_kg)
}

/**
 * Formate un timestamp d'axe en date courte FR.
 * @param value - Timestamp en millisecondes.
 * @returns La date au format JJ/MM.
 */
function formatDateTick(value: number): string {
  return new Date(value).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })
}

/**
 * Formate un nombre éventuellement absent (stat card).
 * @param value - Valeur numérique ou undefined.
 * @returns La valeur arrondie ou un tiret.
 */
function formatNum(value: number | undefined): string {
  if (value === undefined) {
    return '–'
  }
  const num: number = Number(value)
  return Number.isInteger(num) ? String(num) : num.toFixed(1)
}

/**
 * Gabarit HTML de l'infobulle du graphique d'exercice.
 * @param point - Point survolé.
 * @returns Le HTML de l'infobulle.
 */
function exerciseTooltip(point: ExerciseSessionPoint): string {
  const date: string = new Date(point.date).toLocaleDateString('fr-FR')
  return `<div style="font-weight:600">${date}</div>
    <div>1RM : ${formatNum(Number(point.estimated_1rm))} kg</div>
    <div>Charge : ${formatNum(Number(point.top_weight_kg))} kg × ${point.top_set_reps}</div>`
}

/**
 * Gabarit HTML de l'infobulle du graphique de volume.
 * @param point - Point survolé.
 * @returns Le HTML de l'infobulle.
 */
function volumeTooltip(point: VolumePoint): string {
  const date: string = new Date(point.date).toLocaleDateString('fr-FR')
  return `<div style="font-weight:600">${date}</div>
    <div>Volume : ${formatNum(Number(point.total_volume_kg))} kg</div>
    <div>${point.sets_count} série${point.sets_count > 1 ? 's' : ''}</div>`
}

/**
 * Charge la progression de l'exercice sélectionné.
 */
async function loadExerciseProgress(): Promise<void> {
  if (selectedExerciseId.value === undefined) {
    exerciseProgress.value = null
    return
  }
  loadingExercise.value = true
  try {
    exerciseProgress.value = await apiFetch<ExerciseProgress>(`/stats/exercise/${selectedExerciseId.value}`)
  } catch {
    exerciseProgress.value = null
  } finally {
    loadingExercise.value = false
  }
}

/**
 * Charge le volume agrégé selon les filtres muscle / séance.
 */
async function loadVolume(): Promise<void> {
  loadingVolume.value = true
  const query: Record<string, number> = {}
  if (selectedMuscleId.value !== undefined) {
    query.muscle_group_id = selectedMuscleId.value
  }
  if (selectedDayId.value !== undefined) {
    query.workout_day_id = selectedDayId.value
  }
  try {
    volumePoints.value = await apiFetch<VolumePoint[]>('/stats/volume', { query })
  } catch {
    volumePoints.value = []
  } finally {
    loadingVolume.value = false
  }
}

watch(selectedExerciseId, (): void => {
  void loadExerciseProgress()
})

watch([selectedMuscleId, selectedDayId], (): void => {
  void loadVolume()
})

onMounted((): void => {
  void loadVolume()
})
</script>
