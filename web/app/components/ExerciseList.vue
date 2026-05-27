<template>
  <div class="flex flex-col gap-2">
    <div
      v-for="exercise in exercises"
      :key="exercise.id"
      class="border-default bg-elevated/40 flex items-center gap-3 rounded-xl border p-2.5"
    >
      <img
        v-if="exercise.image_path"
        :src="exercise.image_path"
        :alt="exercise.name_fr"
        class="h-14 w-14 shrink-0 rounded-lg object-contain bg-white/90 p-0.5"
        loading="lazy"
      />
      <div v-else class="bg-muted flex h-12 w-12 shrink-0 items-center justify-center rounded-lg">
        <UIcon :name="equipmentIcon(exercise.equipment)" class="text-muted h-5 w-5" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-semibold">{{ exercise.name_fr }}</p>
        <p class="text-muted truncate text-xs">
          {{ groupLabel(exercise.muscle_group_id) }} · {{ equipmentLabel(exercise.equipment) }}
          <span v-if="exercise.is_custom" class="text-primary"> · Perso</span>
        </p>
      </div>
      <div class="flex shrink-0 items-center gap-1">
        <UButton
          v-if="exercise.is_custom"
          color="neutral"
          variant="ghost"
          icon="lucide:pencil"
          size="sm"
          aria-label="Modifier l'exercice"
          @click="emit('edit', exercise)"
        />
        <UButton
          v-if="isAdded(exercise.id)"
          color="primary"
          variant="soft"
          icon="lucide:check"
          size="sm"
          disabled
          aria-label="Déjà ajouté"
        />
        <UButton
          v-else
          color="primary"
          icon="lucide:plus"
          size="sm"
          :loading="addingId === exercise.id"
          aria-label="Ajouter l'exercice"
          @click="emit('add', exercise.id)"
        />
      </div>
    </div>

    <p v-if="exercises.length === 0" class="text-muted py-6 text-center text-sm">
      {{ emptyMessage }}
    </p>
  </div>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue'
import type { Exercise, MuscleGroup } from '~/types/api'
import { equipmentIcon, equipmentLabel } from '~/utils/equipment'

const props = defineProps({
  exercises: {
    type: Array as PropType<Exercise[]>,
    required: true,
  },
  existingExerciseIds: {
    type: Array as PropType<number[]>,
    default: () => [],
  },
  addingId: {
    type: Number as PropType<number | null>,
    default: null,
  },
  muscleGroups: {
    type: Array as PropType<MuscleGroup[]>,
    default: () => [],
  },
  emptyMessage: {
    type: String,
    default: 'Aucun exercice.',
  },
})

const emit = defineEmits<{
  (e: 'add', exerciseId: number): void
  (e: 'edit', exercise: Exercise): void
}>()

/**
 * Indique si un exercice est déjà présent dans le jour de séance.
 * @param exerciseId - Identifiant de l'exercice.
 * @returns `true` si l'exercice est déjà ajouté.
 */
function isAdded(exerciseId: number): boolean {
  return (props.existingExerciseIds ?? []).includes(exerciseId)
}

/**
 * Retourne le nom FR d'un groupe musculaire.
 * @param muscleGroupId - Identifiant du groupe.
 * @returns Le libellé ou une chaîne vide.
 */
function groupLabel(muscleGroupId: number): string {
  return props.muscleGroups.find((group: MuscleGroup) => group.id === muscleGroupId)?.name_fr ?? ''
}
</script>
