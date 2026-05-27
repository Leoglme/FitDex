<template>
  <USlideover
    :open="props.open"
    :title="slideoverTitle"
    :description="slideoverDescription"
    @update:open="(value: boolean) => emit('update:open', value)"
  >
    <template #body>
      <!-- Recherche globale -->
      <div class="mb-4 flex flex-col gap-2">
        <UInput
          v-model="searchQuery"
          icon="lucide:search"
          placeholder="Rechercher un exercice…"
          class="w-full"
          :loading="loadingSearch"
          @update:model-value="onSearchInput"
        />
        <UButton
          v-if="view !== 'search'"
          color="neutral"
          variant="soft"
          icon="lucide:plus"
          block
          @click="openCreateForm"
        >
          Créer un exercice
        </UButton>
      </div>

      <!-- Résultats de recherche -->
      <div v-if="view === 'search'">
        <ExerciseList
          :exercises="searchResults"
          :existing-exercise-ids="existingExerciseIds"
          :adding-id="addingId"
          :muscle-groups="muscleGroups"
          empty-message="Aucun exercice trouvé."
          @add="onAdd"
          @edit="openEditForm"
        />
      </div>

      <!-- Étape 1 : catégories -->
      <div v-else-if="view === 'groups'">
        <div v-if="loadingGroups" class="grid grid-cols-2 gap-3">
          <USkeleton v-for="n in 6" :key="n" class="h-20 w-full rounded-xl" />
        </div>
        <div v-else class="grid grid-cols-2 gap-3">
          <button
            v-for="group in muscleGroups"
            :key="group.id"
            type="button"
            class="hover:border-primary hover:bg-elevated border-default bg-elevated/40 flex flex-col items-center gap-3 rounded-xl border p-4 text-center transition-colors"
            @click="onSelectGroup(group)"
          >
            <div
              class="flex h-16 w-16 items-center justify-center rounded-2xl"
              :class="muscleGroupVisual(group.slug).bgClass"
            >
              <UIcon
                :name="muscleGroupVisual(group.slug).icon"
                class="h-9 w-9"
                :class="muscleGroupVisual(group.slug).iconClass"
              />
            </div>
            <span class="text-sm leading-tight font-semibold">{{ group.name_fr }}</span>
          </button>
        </div>
      </div>

      <!-- Étape 2 : exercices de la catégorie -->
      <div v-else>
        <UButton color="neutral" variant="ghost" icon="lucide:arrow-left" class="mb-3" @click="view = 'groups'">
          Catégories
        </UButton>

        <div v-if="loadingExercises" class="flex flex-col gap-3">
          <USkeleton v-for="n in 5" :key="n" class="h-16 w-full rounded-xl" />
        </div>

        <ExerciseList
          v-else
          :exercises="exercises"
          :existing-exercise-ids="existingExerciseIds"
          :adding-id="addingId"
          :muscle-groups="muscleGroups"
          empty-message="Aucun exercice dans cette catégorie."
          @add="onAdd"
          @edit="openEditForm"
        />
      </div>
    </template>
  </USlideover>

  <ExerciseForm
    v-model:open="formOpen"
    :exercise="editingExercise"
    :muscle-groups="muscleGroups"
    :default-muscle-group-id="selectedGroup?.id ?? null"
    @saved="onExerciseSaved"
  />
</template>

<script lang="ts" setup>
import type { PropType, Ref } from 'vue'
import type { Exercise, MuscleGroup } from '~/types/api'
import type { ExercisePickerProps } from '~/types/ExercisePicker'
import { muscleGroupVisual } from '~/utils/muscleGroupVisual'

/**
 * Définit les props du composant ExercisePicker.
 */
const props: ExercisePickerProps = defineProps({
  open: {
    type: Boolean,
    required: true,
  },
  existingExerciseIds: {
    type: Array as PropType<number[]>,
    default: () => [],
  },
})

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'add', exerciseId: number): void
}>()

const { fetchMuscleGroups, fetchExercises } = useCatalog()
const toast = useToast()

const view: Ref<'groups' | 'exercises' | 'search'> = ref('groups')
const muscleGroups: Ref<MuscleGroup[]> = ref([])
const exercises: Ref<Exercise[]> = ref([])
const searchResults: Ref<Exercise[]> = ref([])
const selectedGroup: Ref<MuscleGroup | null> = ref(null)
const loadingGroups: Ref<boolean> = ref(false)
const loadingExercises: Ref<boolean> = ref(false)
const loadingSearch: Ref<boolean> = ref(false)
const addingId: Ref<number | null> = ref(null)
const searchQuery: Ref<string> = ref('')
const formOpen: Ref<boolean> = ref(false)
const editingExercise: Ref<Exercise | null> = ref(null)

let searchTimer: ReturnType<typeof setTimeout> | null = null

const slideoverTitle = computed((): string => {
  if (view.value === 'search') {
    return 'Recherche'
  }
  if (view.value === 'groups') {
    return 'Choisir une catégorie'
  }
  return selectedGroup.value?.name_fr ?? 'Exercices'
})

const slideoverDescription = computed((): string | undefined => {
  if (view.value === 'groups') {
    return 'Sélectionne un muscle pour voir ses exercices.'
  }
  if (view.value === 'search' && searchQuery.value.trim()) {
    return `${searchResults.value.length} résultat${searchResults.value.length > 1 ? 's' : ''}`
  }
  return undefined
})

/**
 * Charge les groupes musculaires (une seule fois).
 */
async function loadGroups(): Promise<void> {
  if (muscleGroups.value.length > 0) {
    return
  }
  loadingGroups.value = true
  try {
    muscleGroups.value = await fetchMuscleGroups()
  } catch {
    toast.add({ title: 'Impossible de charger les catégories.', color: 'error' })
  } finally {
    loadingGroups.value = false
  }
}

/**
 * Lance une recherche texte avec debounce.
 * @param value - Terme saisi.
 */
function onSearchInput(value: string): void {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  const trimmed = value.trim()
  if (trimmed.length < 2) {
    searchResults.value = []
    if (view.value === 'search') {
      view.value = 'groups'
    }
    return
  }
  view.value = 'search'
  searchTimer = setTimeout((): void => {
    void runSearch(trimmed)
  }, 300)
}

/**
 * Exécute la recherche d'exercices.
 * @param query - Terme de recherche.
 */
async function runSearch(query: string): Promise<void> {
  loadingSearch.value = true
  try {
    searchResults.value = await fetchExercises(null, query)
  } catch {
    toast.add({ title: 'Recherche impossible.', color: 'error' })
  } finally {
    loadingSearch.value = false
  }
}

/**
 * Sélectionne une catégorie et charge ses exercices.
 * @param group - Groupe musculaire choisi.
 */
async function onSelectGroup(group: MuscleGroup): Promise<void> {
  selectedGroup.value = group
  view.value = 'exercises'
  exercises.value = []
  loadingExercises.value = true
  try {
    exercises.value = await fetchExercises(group.id)
  } catch {
    toast.add({ title: 'Impossible de charger les exercices.', color: 'error' })
  } finally {
    loadingExercises.value = false
  }
}

/**
 * Notifie le parent de l'ajout d'un exercice au jour de séance.
 * @param exerciseId - Identifiant de l'exercice à ajouter.
 */
function onAdd(exerciseId: number): void {
  addingId.value = exerciseId
  emit('add', exerciseId)
  void nextTick((): void => {
    addingId.value = null
  })
}

/**
 * Ouvre le formulaire de création d'exercice.
 */
function openCreateForm(): void {
  editingExercise.value = null
  formOpen.value = true
}

/**
 * Ouvre le formulaire d'édition d'un exercice personnalisé.
 * @param exercise - Exercice à modifier.
 */
function openEditForm(exercise: Exercise): void {
  editingExercise.value = exercise
  formOpen.value = true
}

/**
 * Rafraîchit les listes après création ou modification d'un exercice.
 * @param exercise - Exercice enregistré.
 */
function onExerciseSaved(exercise: Exercise): void {
  if (view.value === 'search' && searchQuery.value.trim().length >= 2) {
    void runSearch(searchQuery.value.trim())
  } else if (view.value === 'exercises' && selectedGroup.value?.id === exercise.muscle_group_id) {
    void onSelectGroup(selectedGroup.value)
  }
}

watch(
  (): boolean => props.open,
  (open: boolean): void => {
    if (open) {
      view.value = 'groups'
      searchQuery.value = ''
      searchResults.value = []
      void loadGroups()
    }
  },
  { immediate: true },
)
</script>
