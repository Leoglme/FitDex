<template>
  <div>
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-extrabold">Mes séances</h1>
        <p class="text-muted text-sm">Configure tes jours, puis lance ta séance.</p>
      </div>
      <UButton color="primary" icon="lucide:plus" :loading="creating" @click="onCreateDay">Jour</UButton>
    </div>

    <div v-if="pending" class="mt-6 flex flex-col gap-3">
      <USkeleton v-for="n in 3" :key="n" class="h-24 w-full rounded-xl" />
    </div>

    <div v-else-if="days && days.length > 0" class="mt-6 flex flex-col gap-3">
      <div
        v-for="day in days"
        :key="day.id"
        class="hover:border-primary border-default bg-elevated/40 flex items-center justify-between gap-3 rounded-xl border p-4 transition-colors"
      >
        <NuxtLink :to="`/seances/${day.id}`" class="min-w-0 flex-1">
          <p class="text-lg font-bold">{{ day.name }}</p>
          <p class="text-muted text-sm">
            {{ day.day_exercises.length }} exercice{{ day.day_exercises.length > 1 ? 's' : '' }}
          </p>
        </NuxtLink>
        <UButton
          v-if="day.day_exercises.length > 0"
          color="primary"
          size="sm"
          icon="lucide:play"
          class="shrink-0"
          :to="`/seances/${day.id}?start=1`"
        >
          Lancer
        </UButton>
        <NuxtLink v-else :to="`/seances/${day.id}`" class="shrink-0">
          <UIcon name="lucide:chevron-right" class="text-muted h-5 w-5" />
        </NuxtLink>
      </div>
    </div>

    <div v-else class="mt-10 flex flex-col items-center gap-4 text-center">
      <UIcon name="lucide:dumbbell" class="text-muted h-12 w-12" />
      <div>
        <p class="font-semibold">Aucune séance pour l'instant</p>
        <p class="text-muted text-sm">Crée ton premier jour d'entraînement pour commencer.</p>
      </div>
      <UButton color="primary" size="lg" icon="lucide:plus" :loading="creating" @click="onCreateDay">
        Créer un jour
      </UButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import type { WorkoutDay } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const { apiFetch } = useApi()
const toast = useToast()
const creating: Ref<boolean> = ref(false)

const {
  data: days,
  pending,
  refresh,
} = await useAsyncData<WorkoutDay[]>('workout-days', () => apiFetch<WorkoutDay[]>('/workout-days'), {
  default: () => [],
})

/**
 * Crée un nouveau jour de séance (nommé "Jour N" par défaut) puis rafraîchit la liste.
 */
async function onCreateDay(): Promise<void> {
  creating.value = true
  try {
    await apiFetch<WorkoutDay>('/workout-days', { method: 'POST', body: {} })
    await refresh()
  } catch {
    toast.add({ title: 'Impossible de créer la séance.', color: 'error' })
  } finally {
    creating.value = false
  }
}
</script>
