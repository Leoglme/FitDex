<template>
  <div class="flex flex-col gap-6">
    <div>
      <h1 class="text-2xl font-extrabold">Réglages machines</h1>
      <p class="text-muted text-sm">Sauvegarde tes réglages Basic Fit (siège, écartement…).</p>
    </div>

    <UInput v-model="searchQuery" icon="lucide:search" placeholder="Rechercher une machine…" @update:model-value="onSearch" />

    <div v-if="loading" class="flex flex-col gap-3">
      <USkeleton v-for="n in 5" :key="n" class="h-16 w-full rounded-xl" />
    </div>

    <div v-else class="flex flex-col gap-2">
      <button
        v-for="machine in machines"
        :key="machine.id"
        type="button"
        class="border-default bg-elevated/40 hover:border-primary flex items-center gap-3 rounded-xl border p-3 text-left transition-colors"
        @click="openSetting(machine)"
      >
        <ExerciseImage
          :image-path="machine.image_path"
          :equipment="machine.equipment"
          :alt="machine.name_fr"
        />
        <div class="min-w-0 flex-1">
          <p class="truncate font-semibold">{{ machine.name_fr }}</p>
          <p v-if="savedLabel(machine.id)" class="text-primary text-xs">{{ savedLabel(machine.id) }}</p>
          <p v-else class="text-muted text-xs">Aucun réglage enregistré</p>
        </div>
        <UIcon name="lucide:chevron-right" class="text-muted h-5 w-5 shrink-0" />
      </button>
    </div>

    <UModal
      :open="modalOpen"
      :title="selectedMachine?.name_fr ?? 'Réglages'"
      description="Enregistre les numéros affichés sur la machine."
      @update:open="(value: boolean) => (modalOpen = value)"
    >
      <template #body>
        <div class="flex flex-col gap-4">
          <UFormField label="Hauteur du siège">
            <NativeSelect v-model="seatLevel" :items="levelItems" placeholder="Non renseigné" />
          </UFormField>
          <UFormField label="Écartement / prises">
            <NativeSelect v-model="gripLevel" :items="levelItems" placeholder="Non renseigné" />
          </UFormField>
          <UFormField label="Notes" hint="Facultatif">
            <UInput v-model="notes" placeholder="Ex. Basic Fit Part-Dieu" class="w-full" />
          </UFormField>
        </div>
      </template>
      <template #footer>
        <div class="flex w-full gap-2">
          <UButton color="neutral" variant="ghost" class="flex flex-1 justify-center" @click="modalOpen = false">
            Annuler
          </UButton>
          <UButton color="primary" class="flex flex-1 justify-center" :loading="saving" @click="saveSetting">
            Enregistrer
          </UButton>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef, Ref } from 'vue'
import type { MachineExercise, MachineSetting } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const { fetchMachineExercises, fetchSettings, saveSetting: persistSetting } = useMachines()
const toast = useToast()

const machines: Ref<MachineExercise[]> = ref([])
const settings: Ref<MachineSetting[]> = ref([])
const loading: Ref<boolean> = ref(true)
const searchQuery: Ref<string> = ref('')
const modalOpen: Ref<boolean> = ref(false)
const selectedMachine: Ref<MachineExercise | null> = ref(null)
const seatLevel: Ref<number | ''> = ref('')
const gripLevel: Ref<number | ''> = ref('')
const notes: Ref<string> = ref('')
const saving: Ref<boolean> = ref(false)

let searchTimer: ReturnType<typeof setTimeout> | null = null

const levelItems = [
  { label: '—', value: '' },
  ...Array.from({ length: 9 }, (_, index) => ({
    label: String(index + 1),
    value: index + 1,
  })),
]

const settingsByExercise: ComputedRef<Map<number, MachineSetting>> = computed(() => {
  const map = new Map<number, MachineSetting>()
  for (const setting of settings.value) {
    map.set(setting.exercise_id, setting)
  }
  return map
})

function savedLabel(exerciseId: number): string | null {
  const setting = settingsByExercise.value.get(exerciseId)
  if (!setting) {
    return null
  }
  const parts: string[] = []
  if (setting.seat_level) {
    parts.push(`Siège ${setting.seat_level}`)
  }
  if (setting.grip_level) {
    parts.push(`Écart. ${setting.grip_level}`)
  }
  return parts.length > 0 ? parts.join(' · ') : 'Réglages enregistrés'
}

async function loadData(query?: string): Promise<void> {
  loading.value = true
  try {
    const [machineList, settingList] = await Promise.all([fetchMachineExercises(query), fetchSettings()])
    machines.value = machineList
    settings.value = settingList
  } catch {
    toast.add({ title: 'Impossible de charger les machines.', color: 'error' })
  } finally {
    loading.value = false
  }
}

function onSearch(value: string): void {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout((): void => {
    void loadData(value.trim() || undefined)
  }, 300)
}

function openSetting(machine: MachineExercise): void {
  selectedMachine.value = machine
  const existing = settingsByExercise.value.get(machine.id)
  seatLevel.value = existing?.seat_level ?? ''
  gripLevel.value = existing?.grip_level ?? ''
  notes.value = existing?.notes ?? ''
  modalOpen.value = true
}

async function saveSetting(): Promise<void> {
  if (!selectedMachine.value) {
    return
  }
  saving.value = true
  try {
    const saved = await persistSetting(selectedMachine.value.id, {
      seat_level: seatLevel.value === '' ? null : Number(seatLevel.value),
      grip_level: gripLevel.value === '' ? null : Number(gripLevel.value),
      notes: notes.value.trim() || null,
    })
    const others = settings.value.filter((s) => s.exercise_id !== saved.exercise_id)
    settings.value = [...others, saved]
    modalOpen.value = false
    toast.add({ title: 'Réglages enregistrés.', color: 'success' })
  } catch {
    toast.add({ title: 'Enregistrement impossible.', color: 'error' })
  } finally {
    saving.value = false
  }
}

void loadData()
</script>
