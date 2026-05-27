<template>
  <UModal
    :open="open"
    :title="exercise ? 'Modifier l\'exercice' : 'Nouvel exercice'"
    :description="exercise ? 'Modifie les informations de ton exercice personnalisé.' : 'Crée un exercice qui n\'existe pas encore dans le catalogue.'"
    @update:open="(value: boolean) => emit('update:open', value)"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <UFormField label="Nom">
          <UInput v-model="nameFr" placeholder="Ex. Extension triceps poulie" class="w-full" />
        </UFormField>

        <UFormField label="Catégorie">
          <USelect
            v-model="muscleGroupId"
            :items="muscleGroupItems"
            placeholder="Choisir une catégorie"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Matériel">
          <USelect v-model="equipment" :items="equipmentItems" class="w-full" />
        </UFormField>

        <UFormField label="Description" hint="Facultatif">
          <UTextarea v-model="description" placeholder="Notes, variantes…" :rows="2" class="w-full" />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex w-full gap-2">
        <UButton color="neutral" variant="ghost" class="flex-1" @click="emit('update:open', false)">
          Annuler
        </UButton>
        <UButton color="primary" class="flex-1" :loading="submitting" :disabled="!canSubmit" @click="submit">
          {{ exercise ? 'Enregistrer' : 'Créer' }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<script lang="ts" setup>
import type { ComputedRef, PropType, Ref } from 'vue'
import type { Equipment, Exercise, MuscleGroup } from '~/types/api'
import { equipmentLabel } from '~/utils/equipment'

const props = defineProps({
  open: {
    type: Boolean,
    required: true,
  },
  exercise: {
    type: Object as PropType<Exercise | null>,
    default: null,
  },
  muscleGroups: {
    type: Array as PropType<MuscleGroup[]>,
    default: () => [],
  },
  defaultMuscleGroupId: {
    type: Number as PropType<number | null>,
    default: null,
  },
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved', exercise: Exercise): void
}>()

const { createExercise, updateExercise } = useCatalog()
const toast = useToast()

const nameFr: Ref<string> = ref('')
const muscleGroupId: Ref<number | undefined> = ref(undefined)
const equipment: Ref<Equipment> = ref('machine')
const description: Ref<string> = ref('')
const submitting: Ref<boolean> = ref(false)

const EQUIPMENT_OPTIONS: Equipment[] = ['machine', 'barbell', 'dumbbell', 'cable', 'bodyweight', 'other']

const muscleGroupItems: ComputedRef<{ label: string; value: number }[]> = computed(() =>
  props.muscleGroups.map((group: MuscleGroup) => ({
    label: group.name_fr,
    value: group.id,
  })),
)

const equipmentItems: ComputedRef<{ label: string; value: Equipment }[]> = computed(() =>
  EQUIPMENT_OPTIONS.map((value: Equipment) => ({
    label: equipmentLabel(value),
    value,
  })),
)

const canSubmit: ComputedRef<boolean> = computed(() => nameFr.value.trim().length > 0 && muscleGroupId.value !== undefined)

/**
 * Réinitialise le formulaire à partir de l'exercice en édition ou des valeurs par défaut.
 */
function resetForm(): void {
  if (props.exercise) {
    nameFr.value = props.exercise.name_fr
    muscleGroupId.value = props.exercise.muscle_group_id
    equipment.value = props.exercise.equipment
    description.value = props.exercise.description ?? ''
    return
  }
  nameFr.value = ''
  muscleGroupId.value = props.defaultMuscleGroupId ?? props.muscleGroups[0]?.id
  equipment.value = 'machine'
  description.value = ''
}

/**
 * Crée ou met à jour l'exercice personnalisé.
 */
async function submit(): Promise<void> {
  if (!canSubmit.value || muscleGroupId.value === undefined) {
    return
  }
  submitting.value = true
  try {
    const payload = {
      name_fr: nameFr.value.trim(),
      muscle_group_id: muscleGroupId.value,
      equipment: equipment.value,
      description: description.value.trim() || null,
    }
    const saved = props.exercise
      ? await updateExercise(props.exercise.id, payload)
      : await createExercise(payload)
    toast.add({
      title: props.exercise ? 'Exercice modifié.' : 'Exercice créé.',
      color: 'success',
    })
    emit('saved', saved)
    emit('update:open', false)
  } catch {
    toast.add({ title: 'Impossible d’enregistrer l’exercice.', color: 'error' })
  } finally {
    submitting.value = false
  }
}

watch(
  (): boolean => props.open,
  (open: boolean): void => {
    if (open) {
      resetForm()
    }
  },
  { immediate: true },
)
</script>
