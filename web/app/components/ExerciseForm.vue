<template>
  <UModal
    :open="open"
    :title="exercise ? 'Modifier l\'exercice' : 'Nouvel exercice'"
    :description="exercise ? 'Modifie ton exercice communautaire.' : 'Crée un exercice visible par toute la communauté FitDex.'"
    @update:open="(value: boolean) => emit('update:open', value)"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <UFormField label="Nom">
          <UInput v-model="nameFr" placeholder="Ex. Pec fly Basic Fit" class="w-full" />
        </UFormField>

        <UFormField label="Catégorie">
          <NativeSelect
            v-model="muscleGroupId"
            :items="muscleGroupItems"
            placeholder="Choisir une catégorie"
          />
        </UFormField>

        <UFormField label="Matériel">
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="option in EQUIPMENT_OPTIONS"
              :key="option"
              type="button"
              class="border-default flex flex-col items-center gap-2 rounded-xl border p-3 transition-colors"
              :class="equipment === option ? 'border-primary bg-primary/10' : 'bg-elevated/40'"
              @click="equipment = option"
            >
              <UIcon :name="equipmentIcon(option)" class="h-7 w-7" :class="equipment === option ? 'text-primary' : 'text-muted'" />
              <span class="text-center text-xs font-medium">{{ equipmentLabel(option) }}</span>
            </button>
          </div>
        </UFormField>

        <UFormField v-if="equipment === 'machine'" label="Machine de référence" hint="Facultatif — pré-remplit le nom">
          <div v-if="loadingMachines" class="flex flex-col gap-2">
            <USkeleton v-for="n in 3" :key="n" class="h-14 w-full rounded-xl" />
          </div>
          <div v-else class="max-h-48 overflow-y-auto rounded-xl border border-default">
            <button
              v-for="machine in machineExercises"
              :key="machine.id"
              type="button"
              class="hover:bg-elevated flex w-full items-center gap-3 border-b border-default p-2.5 text-left last:border-b-0"
              @click="applyMachineReference(machine)"
            >
              <ExerciseImage
                :image-path="machine.image_path"
                equipment="machine"
                :alt="machine.name_fr"
                img-class="h-12 w-12 shrink-0 rounded-lg bg-white/90 object-contain p-0.5"
                placeholder-class="h-12 w-12"
              />
              <span class="truncate text-sm font-medium">{{ machine.name_fr }}</span>
            </button>
          </div>
        </UFormField>

        <UFormField v-if="!exercise" label="Image" hint="Facultatif — photo personnelle pour la communauté">
          <div class="flex items-center gap-3">
        <img
          v-if="imagePreview && !previewFailed"
          :src="imagePreview"
          alt="Aperçu"
          class="h-16 w-16 shrink-0 rounded-lg bg-white/90 object-contain p-0.5"
          @error="previewFailed = true"
        />
            <div v-else class="bg-muted flex h-16 w-16 shrink-0 items-center justify-center rounded-lg">
              <UIcon name="lucide:image-plus" class="text-muted h-6 w-6" />
            </div>
            <label class="border-default bg-elevated/40 hover:border-primary flex flex-1 cursor-pointer items-center justify-center rounded-xl border border-dashed px-4 py-3 text-sm font-medium">
              {{ uploadingImage ? 'Envoi…' : 'Ajouter une photo' }}
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onImageSelected" />
            </label>
          </div>
        </UFormField>

        <UFormField label="Description" hint="Facultatif">
          <UTextarea v-model="description" placeholder="Notes, variantes…" :rows="2" class="w-full" />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex w-full gap-2">
        <UButton color="neutral" variant="ghost" class="flex flex-1 justify-center" @click="emit('update:open', false)">
          Annuler
        </UButton>
        <UButton
          color="primary"
          class="flex flex-1 justify-center"
          :loading="submitting"
          :disabled="!canSubmit"
          @click="submit"
        >
          {{ exercise ? 'Enregistrer' : 'Créer' }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>

<script lang="ts" setup>
import type { ComputedRef, PropType, Ref } from 'vue'
import type { Equipment, Exercise, MachineExercise, MuscleGroup } from '~/types/api'
import { equipmentIcon, equipmentLabel } from '~/utils/equipment'
import { resolveMediaUrl } from '~/utils/mediaUrl'

const props = defineProps({
  open: { type: Boolean, required: true },
  exercise: { type: Object as PropType<Exercise | null>, default: null },
  muscleGroups: { type: Array as PropType<MuscleGroup[]>, default: () => [] },
  defaultMuscleGroupId: { type: Number as PropType<number | null>, default: null },
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved', exercise: Exercise): void
}>()

const { createExercise, updateExercise, uploadExerciseImage } = useCatalog()
const { fetchMachineExercises } = useMachines()
const toast = useToast()

const nameFr: Ref<string> = ref('')
const muscleGroupId: Ref<number | undefined> = ref(undefined)
const equipment: Ref<Equipment> = ref('machine')
const description: Ref<string> = ref('')
const imagePath: Ref<string | null> = ref(null)
const imagePreview: Ref<string | null> = ref(null)
const submitting: Ref<boolean> = ref(false)
const uploadingImage: Ref<boolean> = ref(false)
const previewFailed: Ref<boolean> = ref(false)
const machineExercises: Ref<MachineExercise[]> = ref([])
const loadingMachines: Ref<boolean> = ref(false)

const EQUIPMENT_OPTIONS: Equipment[] = ['machine', 'barbell', 'dumbbell', 'cable', 'bodyweight', 'other']

const muscleGroupItems: ComputedRef<{ label: string; value: number }[]> = computed(() =>
  props.muscleGroups.map((group: MuscleGroup) => ({ label: group.name_fr, value: group.id })),
)

const canSubmit: ComputedRef<boolean> = computed(() => nameFr.value.trim().length > 0 && muscleGroupId.value !== undefined)

async function loadMachineExercises(): Promise<void> {
  loadingMachines.value = true
  try {
    machineExercises.value = await fetchMachineExercises()
  } catch {
    machineExercises.value = []
  } finally {
    loadingMachines.value = false
  }
}

function resetForm(): void {
  if (props.exercise) {
    nameFr.value = props.exercise.name_fr
    muscleGroupId.value = props.exercise.muscle_group_id
    equipment.value = props.exercise.equipment
    description.value = props.exercise.description ?? ''
    imagePath.value = props.exercise.image_path
    imagePreview.value = resolveMediaUrl(props.exercise.image_path)
    previewFailed.value = false
    return
  }
  nameFr.value = ''
  muscleGroupId.value = props.defaultMuscleGroupId ?? props.muscleGroups[0]?.id
  equipment.value = 'machine'
  description.value = ''
  imagePath.value = null
  imagePreview.value = null
  previewFailed.value = false
}

function applyMachineReference(machine: MachineExercise): void {
  if (!nameFr.value.trim()) {
    nameFr.value = machine.name_fr
  }
  if (!imagePath.value && machine.image_path) {
    imagePath.value = machine.image_path
    imagePreview.value = resolveMediaUrl(machine.image_path)
  }
}

async function onImageSelected(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) {
    return
  }
  uploadingImage.value = true
  try {
    imagePath.value = await uploadExerciseImage(file)
    imagePreview.value = resolveMediaUrl(imagePath.value)
    previewFailed.value = false
  } catch {
    toast.add({ title: 'Impossible d’envoyer l’image.', color: 'error' })
  } finally {
    uploadingImage.value = false
    input.value = ''
  }
}

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
      image_path: imagePath.value,
    }
    const saved = props.exercise ? await updateExercise(props.exercise.id, payload) : await createExercise(payload)
    toast.add({ title: props.exercise ? 'Exercice modifié.' : 'Exercice créé pour la communauté.', color: 'success' })
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
      void loadMachineExercises()
    }
  },
  { immediate: true },
)

watch(equipment, (value: Equipment): void => {
  if (value === 'machine' && props.open && machineExercises.value.length === 0) {
    void loadMachineExercises()
  }
})
</script>
