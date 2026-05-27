<template>
  <div>
    <div class="flex items-center gap-2">
      <UButton color="neutral" variant="ghost" icon="lucide:arrow-left" to="/" aria-label="Retour" />

      <!-- Renommage inline du jour de séance -->
      <div v-if="isEditing" class="flex flex-1 items-center gap-2">
        <UInput v-model="nameDraft" autofocus class="flex-1" placeholder="Nom de la séance" @keyup.enter="saveName" />
        <UButton color="primary" icon="lucide:check" :loading="savingName" aria-label="Valider" @click="saveName" />
        <UButton color="neutral" variant="ghost" icon="lucide:x" aria-label="Annuler" @click="isEditing = false" />
      </div>

      <div v-else class="flex flex-1 items-center gap-2">
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-xl font-extrabold">{{ day?.name ?? 'Séance' }}</h1>
          <p class="text-muted text-sm">
            {{ day?.day_exercises.length ?? 0 }} exercice{{ (day?.day_exercises.length ?? 0) > 1 ? 's' : '' }}
          </p>
        </div>
        <UButton
          v-if="day && !sessionActive"
          color="neutral"
          variant="ghost"
          icon="lucide:settings-2"
          aria-label="Modifier le jour"
          :to="`/seances/${dayId}/edit`"
        />
        <UButton
          v-if="day"
          color="neutral"
          variant="ghost"
          icon="lucide:pencil"
          aria-label="Renommer la séance"
          @click="startEdit"
        />
      </div>
    </div>

    <div v-if="pending" class="mt-6 flex flex-col gap-3">
      <USkeleton v-for="n in 3" :key="n" class="h-20 w-full rounded-xl" />
    </div>

    <template v-else-if="day">
      <!-- Bandeau séance active -->
      <div
        v-if="sessionActive && day.day_exercises.length > 0"
        class="border-primary/40 bg-primary/10 mt-4 rounded-xl border px-4 py-3"
      >
        <div class="flex items-center justify-between gap-2">
          <p class="text-sm font-semibold">Séance en cours</p>
          <span class="text-muted text-xs">
            {{ loggedExerciseIds.length }} / {{ day.day_exercises.length }}
          </span>
        </div>
        <div class="bg-elevated mt-2 h-1.5 overflow-hidden rounded-full">
          <div
            class="bg-primary h-full rounded-full transition-all duration-500"
            :style="{ width: `${sessionProgressPercent}%` }"
          />
        </div>
        <p class="text-muted mt-2 text-xs">Tape un exercice pour saisir tes séries.</p>
      </div>

      <div v-if="day.day_exercises.length > 0" class="mt-6 flex flex-col gap-3">
        <div
          v-for="de in day.day_exercises"
          :key="de.id"
          role="button"
          tabindex="0"
          class="hover:border-primary group bg-elevated/40 flex items-center gap-3 rounded-xl border p-3 transition-colors"
          :class="exerciseCardClass(de.exercise.id)"
          @click="onExerciseClick(de.exercise)"
          @keyup.enter="onExerciseClick(de.exercise)"
        >
          <ExerciseImage
            :image-path="de.exercise.image_path"
            :equipment="de.exercise.equipment"
            :alt="de.exercise.name_fr"
            img-class="h-16 w-16 shrink-0 rounded-lg object-contain bg-white/90 p-0.5"
            placeholder-class="h-14 w-14"
          />

          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold">{{ de.exercise.name_fr }}</p>
            <p class="text-muted text-xs">{{ equipmentLabel(de.exercise.equipment) }}</p>
          </div>

          <UIcon
            v-if="loggedExerciseIds.includes(de.exercise.id)"
            name="lucide:circle-check-big"
            class="text-primary h-5 w-5 shrink-0"
          />
        </div>
      </div>

      <div v-else class="mt-10 flex flex-col items-center gap-3 text-center">
        <UIcon name="lucide:list-plus" class="text-muted h-10 w-10" />
        <p class="text-muted text-sm">Aucun exercice. Ajoute-en pour démarrer ta séance.</p>
      </div>

      <div class="mt-6 flex flex-col gap-3">
        <UButton
          v-if="!sessionActive && day.day_exercises.length > 0"
          color="primary"
          size="xl"
          block
          icon="lucide:play"
          class="fitdex-launch-pulse"
          @click="launchSession"
        >
          Lancer la séance
        </UButton>
        <UButton
          v-if="!sessionActive"
          color="neutral"
          variant="subtle"
          size="lg"
          block
          icon="lucide:plus"
          @click="pickerOpen = true"
        >
          Ajouter un exercice
        </UButton>
        <UButton
          v-else
          color="neutral"
          variant="subtle"
          size="lg"
          block
          icon="lucide:plus"
          @click="pickerOpen = true"
        >
          Ajouter un exercice
        </UButton>
        <UButton
          v-if="sessionActive && loggedExerciseIds.length > 0"
          color="primary"
          size="lg"
          block
          icon="lucide:party-popper"
          @click="finishSession"
        >
          Terminer la séance
        </UButton>
      </div>
    </template>

    <div v-else class="text-muted mt-10 text-center">Séance introuvable.</div>

    <!-- Sélection d'exercices par catégorie -->
    <ExercisePicker v-model:open="pickerOpen" :existing-exercise-ids="existingExerciseIds" @add="addExercise" />

    <!-- Tunnel de saisie reps + charge -->
    <TunnelLogger
      v-model:open="tunnelOpen"
      :exercise="tunnelExercise"
      :workout-day-id="dayId"
      :session-id="currentSessionId"
      @logged="onLogged"
    />

    <!-- Célébration de fin de séance -->
    <SuccessBurst
      :show="successOpen"
      title="Séance terminée !"
      :subtitle="celebrationSubtitle"
      @close="onCelebrationClose"
    />
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef, Ref } from 'vue'
import type { Exercise, WorkoutDay, WorkoutSession } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { apiFetch } = useApi()

const dayId: ComputedRef<number> = computed(() => Number(route.params.id))
const shouldAutoStart: ComputedRef<boolean> = computed(() => route.query.start === '1')

const {
  data: days,
  pending,
  refresh,
} = await useAsyncData<WorkoutDay[]>(
  () => `workout-day-${dayId.value}`,
  () => apiFetch<WorkoutDay[]>('/workout-days'),
  { default: () => [], watch: [dayId] },
)

const day: ComputedRef<WorkoutDay | undefined> = computed(() =>
  (days.value ?? []).find((d: WorkoutDay) => d.id === dayId.value),
)

const existingExerciseIds: ComputedRef<number[]> = computed(() =>
  (day.value?.day_exercises ?? []).map((de) => de.exercise.id),
)

// État de renommage
const isEditing: Ref<boolean> = ref(false)
const nameDraft: Ref<string> = ref('')
const savingName: Ref<boolean> = ref(false)

// État picker / tunnel / célébration
const pickerOpen: Ref<boolean> = ref(false)
const tunnelOpen: Ref<boolean> = ref(false)
const tunnelExercise: Ref<Exercise | null> = ref(null)
const currentSessionId: Ref<number | null> = ref(null)
const sessionActive: Ref<boolean> = ref(false)
const loggedExerciseIds: Ref<number[]> = ref([])
const successOpen: Ref<boolean> = ref(false)

const sessionProgressPercent: ComputedRef<number> = computed(() => {
  const total: number = day.value?.day_exercises.length ?? 0
  if (total === 0) {
    return 0
  }
  return Math.round((loggedExerciseIds.value.length / total) * 100)
})

const celebrationSubtitle: ComputedRef<string> = computed(() => {
  const count: number = loggedExerciseIds.value.length
  return `${count} exercice${count > 1 ? 's' : ''} validé${count > 1 ? 's' : ''} 💪`
})

/**
 * Passe le titre en mode édition avec le nom courant pré-rempli.
 */
function startEdit(): void {
  nameDraft.value = day.value?.name ?? ''
  isEditing.value = true
}

/**
 * Enregistre le nouveau nom du jour de séance.
 */
async function saveName(): Promise<void> {
  const name: string = nameDraft.value.trim()
  if (name.length === 0) {
    isEditing.value = false
    return
  }
  savingName.value = true
  try {
    await apiFetch<WorkoutDay>(`/workout-days/${dayId.value}`, { method: 'PATCH', body: { name } })
    await refresh()
    isEditing.value = false
  } catch {
    toast.add({ title: 'Renommage impossible.', color: 'error' })
  } finally {
    savingName.value = false
  }
}

/**
 * Ajoute un exercice au jour de séance puis rafraîchit la liste.
 * @param exerciseId - Identifiant de l'exercice à ajouter.
 */
async function addExercise(exerciseId: number): Promise<void> {
  try {
    await apiFetch<WorkoutDay>(`/workout-days/${dayId.value}/exercises`, {
      method: 'POST',
      body: { exercise_id: exerciseId },
    })
    await refresh()
  } catch {
    toast.add({ title: 'Ajout impossible.', color: 'error' })
  }
}

/**
 * Démarre le mode séance active (bouton « Lancer la séance »).
 */
function launchSession(): void {
  if ((day.value?.day_exercises.length ?? 0) === 0) {
    return
  }
  sessionActive.value = true
  loggedExerciseIds.value = []
  currentSessionId.value = null
}

/**
 * Classes visuelles d'une carte exercice selon l'état de la séance.
 * @param exerciseId - Identifiant de l'exercice.
 * @returns Les classes Tailwind à appliquer.
 */
function exerciseCardClass(exerciseId: number): string {
  if (loggedExerciseIds.value.includes(exerciseId)) {
    return 'border-primary/60'
  }
  if (sessionActive.value) {
    return 'border-default ring-primary/30 ring-2'
  }
  return 'border-default'
}

/**
 * Ouvre le tunnel si la séance est lancée, sinon invite à lancer.
 * @param exercise - Exercice ciblé.
 */
function onExerciseClick(exercise: Exercise): void {
  if (!sessionActive.value) {
    toast.add({
      title: 'Lance d’abord ta séance',
      description: 'Appuie sur « Lancer la séance » pour commencer la saisie.',
      color: 'warning',
    })
    return
  }
  startTunnel(exercise)
}

/**
 * Ouvre le tunnel de saisie pour un exercice donné.
 * @param exercise - Exercice à saisir.
 */
function startTunnel(exercise: Exercise): void {
  tunnelExercise.value = exercise
  tunnelOpen.value = true
}

/**
 * Réceptionne une séance enregistrée : conserve l'id de séance et marque l'exercice comme fait.
 * @param session - Séance renvoyée par l'API.
 */
function onLogged(session: WorkoutSession): void {
  currentSessionId.value = session.id
  const exerciseId: number | null = tunnelExercise.value?.id ?? null
  if (exerciseId !== null && !loggedExerciseIds.value.includes(exerciseId)) {
    loggedExerciseIds.value = [...loggedExerciseIds.value, exerciseId]
  }
}

/**
 * Affiche la célébration de fin de séance.
 */
function finishSession(): void {
  successOpen.value = true
}

/**
 * Ferme la célébration, réinitialise la séance et retourne à l'accueil.
 */
function onCelebrationClose(): void {
  successOpen.value = false
  sessionActive.value = false
  currentSessionId.value = null
  loggedExerciseIds.value = []
  void router.push('/')
}

watch(
  [shouldAutoStart, day],
  ([autoStart, currentDay]: [boolean, WorkoutDay | undefined]): void => {
    if (autoStart && currentDay && currentDay.day_exercises.length > 0 && !sessionActive.value) {
      launchSession()
    }
  },
  { immediate: true },
)
</script>

<style scoped>
@keyframes fitdex-launch-pulse-keyframes {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgb(132 204 22 / 0.45);
  }
  50% {
    box-shadow: 0 0 0 10px rgb(132 204 22 / 0);
  }
}

.fitdex-launch-pulse {
  animation: fitdex-launch-pulse-keyframes 2s ease-in-out infinite;
}
</style>
