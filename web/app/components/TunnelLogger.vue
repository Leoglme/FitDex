<template>
  <Transition name="fitdex-tunnel">
    <div
      v-if="props.open && props.exercise"
      class="bg-default fixed inset-0 z-50 flex flex-col"
      role="dialog"
      aria-modal="true"
    >
      <!-- En-tête : exercice + progression + fermeture -->
      <header class="border-default flex items-center gap-3 border-b px-4 py-3">
        <UButton color="neutral" variant="ghost" icon="lucide:x" aria-label="Quitter le tunnel" @click="close" />
        <img
          v-if="props.exercise.image_path"
          :src="props.exercise.image_path"
          :alt="props.exercise.name_fr"
          class="h-12 w-12 shrink-0 rounded-lg object-contain bg-white/90 p-0.5"
        />
        <div class="min-w-0 flex-1">
          <p class="truncate text-base font-extrabold">{{ props.exercise.name_fr }}</p>
          <p class="text-muted text-xs">
            {{ mode === 'count' ? 'Combien de séries ?' : `Série ${currentSet} / ${setCount}` }}
          </p>
        </div>
      </header>

      <!-- Barre de progression des séries -->
      <div v-if="mode === 'set'" class="flex gap-1.5 px-4 pt-3">
        <span
          v-for="n in setCount"
          :key="n"
          class="h-1.5 flex-1 rounded-full transition-colors"
          :class="n < currentSet ? 'bg-primary' : n === currentSet ? 'bg-primary/50' : 'bg-elevated'"
        />
      </div>

      <main class="flex flex-1 flex-col items-center justify-center px-6">
        <!-- Étape 1 : nombre de séries -->
        <template v-if="mode === 'count'">
          <p class="text-muted mb-2 text-sm">Nombre de séries</p>
          <div class="flex items-center gap-4">
            <UButton
              color="neutral"
              variant="soft"
              size="xl"
              icon="lucide:minus"
              aria-label="Une série de moins"
              @click="setCount = Math.max(1, setCount - 1)"
            />
            <UInput
              v-model="setCountModel"
              type="number"
              inputmode="numeric"
              :ui="{ base: 'w-28' }"
              class="tunnel-input"
              aria-label="Nombre de séries"
            />
            <UButton
              color="neutral"
              variant="soft"
              size="xl"
              icon="lucide:plus"
              aria-label="Une série de plus"
              @click="setCount = Math.min(20, setCount + 1)"
            />
          </div>
          <p v-if="lastInfo" class="text-muted mt-6 text-center text-sm">
            Dernière fois : {{ lastSummary }}
          </p>
        </template>

        <!-- Étape 2 : saisie reps + charge pour la série courante -->
        <template v-else-if="mode === 'set'">
          <div class="grid w-full max-w-md grid-cols-2 gap-4">
            <div class="flex flex-col items-center">
              <p class="text-muted mb-2 text-sm">Répétitions</p>
              <UInput
                v-model="currentRepsModel"
                type="number"
                inputmode="numeric"
                :ui="{ base: 'w-full' }"
                class="tunnel-input"
                aria-label="Nombre de répétitions"
              />
              <div class="mt-3 flex gap-2">
                <UButton color="neutral" variant="soft" size="sm" @click="addReps(-1)">−1</UButton>
                <UButton color="neutral" variant="soft" size="sm" @click="addReps(1)">+1</UButton>
              </div>
            </div>
            <div class="flex flex-col items-center">
              <p class="text-muted mb-2 text-sm">Charge (kg)</p>
              <UInput
                v-model="currentWeightModel"
                type="number"
                inputmode="decimal"
                step="0.5"
                :ui="{ base: 'w-full' }"
                class="tunnel-input"
                aria-label="Charge en kilogrammes"
              />
              <div class="mt-3 flex gap-2">
                <UButton color="neutral" variant="soft" size="sm" @click="addWeight(-2.5)">−2.5</UButton>
                <UButton color="neutral" variant="soft" size="sm" @click="addWeight(2.5)">+2.5</UButton>
              </div>
            </div>
          </div>

          <p v-if="lastInfo" class="text-muted mt-6 text-center text-sm">
            Dernière fois : {{ lastSummary }}
          </p>

          <!-- Récap des séries déjà saisies -->
          <div v-if="currentSet > 1" class="mt-6 flex flex-wrap justify-center gap-2">
            <span v-for="n in currentSet - 1" :key="n" class="bg-elevated rounded-full px-3 py-1 text-xs font-medium">
              S{{ n }} · {{ sets[n - 1]?.reps }}×{{ formatWeight(sets[n - 1]?.weight ?? 0) }}
            </span>
          </div>
        </template>

        <!-- Étape 3 : confirmation animée -->
        <template v-else>
          <div class="relative flex flex-col items-center gap-4">
            <span class="fitdex-success-ring absolute top-10 left-1/2 -translate-x-1/2 rounded-full" />
            <div
              class="fitdex-success-pop fitdex-success-glow bg-primary flex h-24 w-24 items-center justify-center rounded-full text-black"
            >
              <UIcon name="lucide:check" class="h-14 w-14" />
            </div>
            <p class="fitdex-success-pop text-xl font-extrabold">Série validée 💪</p>
          </div>
        </template>
      </main>

      <!-- Action principale (pas de bouton "valider" : la dernière série soumet automatiquement) -->
      <footer v-if="mode !== 'success'" class="border-default border-t p-4">
        <UButton color="primary" size="xl" block :icon="primaryIcon" :loading="submitting" @click="onPrimary">
          {{ primaryLabel }}
        </UButton>
      </footer>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
import type { ComputedRef, PropType, Ref } from 'vue'
import type { Exercise, LastExerciseLog, WorkoutSession } from '~/types/api'
import type { TunnelLoggerProps } from '~/types/TunnelLogger'

/** Une série en cours de saisie. */
interface DraftSet {
  reps: number
  weight: number
}

/** Dernière performance connue sur l'exercice. */
interface LastInfo {
  setsCount: number
  reps: number
  weight: number
  uniform: boolean
}

/**
 * Définit les props du composant TunnelLogger.
 */
const props: TunnelLoggerProps = defineProps({
  open: {
    type: Boolean,
    required: true,
  },
  exercise: {
    type: Object as PropType<Exercise | null>,
    default: null,
  },
  workoutDayId: {
    type: Number,
    required: true,
  },
  sessionId: {
    type: Number as PropType<number | null>,
    default: null,
  },
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'logged', session: WorkoutSession): void
}>()

const { apiFetch } = useApi()
const toast = useToast()

const mode: Ref<'count' | 'set' | 'success'> = ref('count')
const setCount: Ref<number> = ref(3)
const currentSet: Ref<number> = ref(1)
const sets: Ref<DraftSet[]> = ref([])
const submitting: Ref<boolean> = ref(false)
const lastInfo: Ref<LastInfo | null> = ref(null)
const lastSets: Ref<DraftSet[] | null> = ref(null)

/**
 * Modèle string ↔ number pour l'input du nombre de séries.
 */
const setCountModel: ComputedRef<string | number> = computed({
  get: (): number => setCount.value,
  set: (value: string | number): void => {
    setCount.value = clampInt(Number(value), 1, 20)
  },
})

/**
 * Reps de la série courante (coercition entière).
 */
const currentRepsModel: ComputedRef<string | number> = computed({
  get: (): number => sets.value[currentSet.value - 1]?.reps ?? 0,
  set: (value: string | number): void => {
    const draft: DraftSet | undefined = sets.value[currentSet.value - 1]
    if (draft) {
      draft.reps = clampInt(Number(value), 0, 9999)
    }
  },
})

/**
 * Charge de la série courante (coercition décimale).
 */
const currentWeightModel: ComputedRef<string | number> = computed({
  get: (): number => sets.value[currentSet.value - 1]?.weight ?? 0,
  set: (value: string | number): void => {
    const draft: DraftSet | undefined = sets.value[currentSet.value - 1]
    if (draft) {
      draft.weight = Math.max(0, Math.round(Number(value) * 100) / 100 || 0)
    }
  },
})

const primaryLabel: ComputedRef<string> = computed(() => {
  if (mode.value === 'count') {
    return 'Commencer'
  }
  return currentSet.value < setCount.value ? 'Série suivante' : "Terminer l'exercice"
})

const primaryIcon: ComputedRef<string> = computed(() => {
  if (mode.value === 'count') {
    return 'lucide:play'
  }
  return currentSet.value < setCount.value ? 'lucide:arrow-right' : 'lucide:check'
})

const lastSummary: ComputedRef<string> = computed(() => {
  if (!lastInfo.value) {
    return ''
  }
  const { setsCount, reps, weight, uniform } = lastInfo.value
  const setsLabel = `${setsCount} série${setsCount > 1 ? 's' : ''}`
  if (uniform) {
    return `${setsLabel} · ${reps} reps × ${formatWeight(weight)} kg`
  }
  return `${setsLabel} enregistrées`
})

/**
 * Borne et arrondit un entier dans un intervalle.
 * @param value - Valeur brute.
 * @param min - Borne minimale.
 * @param max - Borne maximale.
 * @returns L'entier borné.
 */
function clampInt(value: number, min: number, max: number): number {
  if (Number.isNaN(value)) {
    return min
  }
  return Math.min(max, Math.max(min, Math.round(value)))
}

/**
 * Formate une charge sans décimales superflues (40, 42.5…).
 * @param weight - Charge en kg.
 * @returns La charge formatée.
 */
function formatWeight(weight: number): string {
  return Number.isInteger(weight) ? String(weight) : weight.toFixed(1)
}

/**
 * Incrémente les répétitions de la série courante.
 * @param delta - Variation (peut être négative).
 */
function addReps(delta: number): void {
  currentRepsModel.value = (sets.value[currentSet.value - 1]?.reps ?? 0) + delta
}

/**
 * Incrémente la charge de la série courante.
 * @param delta - Variation en kg (peut être négative).
 */
function addWeight(delta: number): void {
  currentWeightModel.value = (sets.value[currentSet.value - 1]?.weight ?? 0) + delta
}

/**
 * Déclenche un léger retour haptique si disponible.
 */
function vibrate(): void {
  if (typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function') {
    navigator.vibrate(15)
  }
}

/**
 * Charge la dernière saisie complète pour pré-remplir séries, reps et charge.
 */
async function loadLast(): Promise<void> {
  lastInfo.value = null
  lastSets.value = null
  if (!props.exercise) {
    return
  }
  try {
    const last: LastExerciseLog | null = await apiFetch<LastExerciseLog | null>(
      `/sessions/last-exercise/${props.exercise.id}`,
    )
    if (!last?.sets.length) {
      return
    }
    const drafts: DraftSet[] = last.sets.map(
      (set): DraftSet => ({
        reps: set.reps,
        weight: Number(set.weight_kg),
      }),
    )
    lastSets.value = drafts
    setCount.value = drafts.length

    const first = drafts[0]!
    const uniform = drafts.every(
      (set: DraftSet): boolean => set.reps === first.reps && set.weight === first.weight,
    )
    lastInfo.value = {
      setsCount: drafts.length,
      reps: first.reps,
      weight: first.weight,
      uniform,
    }
  } catch {
    // Pas bloquant : on démarre sans historique.
  }
}

/**
 * (Ré)initialise le tunnel à l'ouverture d'un exercice.
 */
function reset(): void {
  mode.value = 'count'
  currentSet.value = 1
  sets.value = []
  submitting.value = false
  setCount.value = 3
  void loadLast()
}

/**
 * Prépare les séries pré-remplies à partir de la dernière saisie complète.
 */
function startSets(): void {
  const fallback: DraftSet = { reps: 10, weight: 20 }
  sets.value = Array.from({ length: setCount.value }, (_, index: number): DraftSet => {
    const previous = lastSets.value?.[index]
    if (previous) {
      return { reps: previous.reps, weight: previous.weight }
    }
    const last = lastSets.value?.at(-1)
    if (last) {
      return { reps: last.reps, weight: last.weight }
    }
    return { ...fallback }
  })
  currentSet.value = 1
  mode.value = 'set'
}

/**
 * Action du bouton principal : avance dans le tunnel ou soumet à la dernière série.
 */
function onPrimary(): void {
  vibrate()
  if (mode.value === 'count') {
    startSets()
    return
  }
  if (currentSet.value < setCount.value) {
    // Reporte les valeurs de la série courante sur la suivante (gain de saisie).
    const current: DraftSet | undefined = sets.value[currentSet.value - 1]
    const nextDraft: DraftSet | undefined = sets.value[currentSet.value]
    if (current && nextDraft) {
      nextDraft.reps = current.reps
      nextDraft.weight = current.weight
    }
    currentSet.value += 1
    return
  }
  void submit()
}

/**
 * Enregistre toutes les séries de l'exercice et déclenche l'animation de succès.
 */
async function submit(): Promise<void> {
  if (!props.exercise) {
    return
  }
  submitting.value = true
  try {
    const session: WorkoutSession = await apiFetch<WorkoutSession>('/sessions/log-exercise', {
      method: 'POST',
      body: {
        exercise_id: props.exercise.id,
        workout_day_id: props.workoutDayId,
        session_id: props.sessionId,
        sets: sets.value.map((draft: DraftSet, index: number) => ({
          set_number: index + 1,
          reps: draft.reps,
          weight_kg: draft.weight,
        })),
      },
    })
    vibrate()
    mode.value = 'success'
    window.setTimeout((): void => {
      emit('logged', session)
      emit('update:open', false)
    }, 1100)
  } catch {
    toast.add({ title: 'Échec de l’enregistrement.', color: 'error' })
    submitting.value = false
  }
}

/**
 * Ferme le tunnel sans enregistrer.
 */
function close(): void {
  emit('update:open', false)
}

watch(
  (): boolean => props.open,
  (open: boolean): void => {
    if (open) {
      reset()
    }
  },
  { immediate: true },
)
</script>

<style scoped>
.fitdex-tunnel-enter-active,
.fitdex-tunnel-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.fitdex-tunnel-enter-from,
.fitdex-tunnel-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
