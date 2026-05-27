<template>
  <div>
    <div class="flex items-center gap-2">
      <UButton color="neutral" variant="ghost" icon="lucide:arrow-left" :to="`/seances/${dayId}`" aria-label="Retour" />
      <div class="min-w-0 flex-1">
        <h1 class="truncate text-xl font-extrabold">Modifier {{ day?.name ?? 'la séance' }}</h1>
        <p class="text-muted text-sm">Gère les exercices de ce jour.</p>
      </div>
    </div>

    <div v-if="pending" class="mt-6 flex flex-col gap-3">
      <USkeleton v-for="n in 3" :key="n" class="h-20 w-full rounded-xl" />
    </div>

    <template v-else-if="day">
      <div v-if="day.day_exercises.length > 0" class="mt-6 flex flex-col gap-3">
        <div
          v-for="de in day.day_exercises"
          :key="de.id"
          class="border-default bg-elevated/40 flex items-center gap-3 rounded-xl border p-3"
        >
          <img
            v-if="resolveMediaUrl(de.exercise.image_path)"
            :src="resolveMediaUrl(de.exercise.image_path)!"
            :alt="de.exercise.name_fr"
            class="h-14 w-14 shrink-0 rounded-lg bg-white/90 object-contain p-0.5"
            loading="lazy"
          />
          <div v-else class="bg-muted flex h-12 w-12 shrink-0 items-center justify-center rounded-lg">
            <UIcon :name="equipmentIcon(de.exercise.equipment)" class="text-muted h-5 w-5" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold">{{ de.exercise.name_fr }}</p>
            <p class="text-muted text-xs">{{ equipmentLabel(de.exercise.equipment) }}</p>
          </div>
          <UButton
            color="error"
            variant="soft"
            icon="lucide:trash-2"
            size="sm"
            aria-label="Supprimer l'exercice"
            @click="removeExercise(de.id)"
          />
        </div>
      </div>

      <div v-else class="mt-10 flex flex-col items-center gap-3 text-center">
        <UIcon name="lucide:list-plus" class="text-muted h-10 w-10" />
        <p class="text-muted text-sm">Aucun exercice dans ce jour.</p>
      </div>

      <UButton color="primary" size="lg" block icon="lucide:plus" class="mt-6" @click="pickerOpen = true">
        Ajouter un exercice
      </UButton>
    </template>

    <ExercisePicker v-model:open="pickerOpen" :existing-exercise-ids="existingExerciseIds" @add="addExercise" />
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef, Ref } from 'vue'
import type { WorkoutDay } from '~/types/api'
import { resolveMediaUrl } from '~/utils/mediaUrl'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const toast = useToast()
const { apiFetch } = useApi()

const dayId: ComputedRef<number> = computed(() => Number(route.params.id))

const { data: days, pending, refresh } = await useAsyncData<WorkoutDay[]>(
  () => `workout-day-edit-${dayId.value}`,
  () => apiFetch<WorkoutDay[]>('/workout-days'),
  { default: () => [], watch: [dayId] },
)

const day: ComputedRef<WorkoutDay | undefined> = computed(() =>
  (days.value ?? []).find((d: WorkoutDay) => d.id === dayId.value),
)

const existingExerciseIds: ComputedRef<number[]> = computed(() =>
  (day.value?.day_exercises ?? []).map((de) => de.exercise.id),
)

const pickerOpen: Ref<boolean> = ref(false)

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

async function removeExercise(dayExerciseId: number): Promise<void> {
  try {
    await apiFetch(`/workout-days/${dayId.value}/exercises/${dayExerciseId}`, { method: 'DELETE' })
    await refresh()
  } catch {
    toast.add({ title: 'Suppression impossible.', color: 'error' })
  }
}
</script>
