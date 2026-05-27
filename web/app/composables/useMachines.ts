import type { MachineExercise, MachineSetting, MachineSettingInput } from '~/types/api'

/**
 * Accès aux réglages machines (Basic Fit, etc.).
 */
export function useMachines(): {
  fetchMachineExercises: (query?: string) => Promise<MachineExercise[]>
  fetchSettings: () => Promise<MachineSetting[]>
  fetchSetting: (exerciseId: number) => Promise<MachineSetting | null>
  saveSetting: (exerciseId: number, input: MachineSettingInput) => Promise<MachineSetting>
} {
  const { apiFetch } = useApi()

  async function fetchMachineExercises(query?: string): Promise<MachineExercise[]> {
    const params: Record<string, string> = {}
    const trimmed = query?.trim()
    if (trimmed) {
      params.q = trimmed
    }
    return apiFetch<MachineExercise[]>('/machines/exercises', { query: params })
  }

  async function fetchSettings(): Promise<MachineSetting[]> {
    return apiFetch<MachineSetting[]>('/machines/settings')
  }

  async function fetchSetting(exerciseId: number): Promise<MachineSetting | null> {
    return apiFetch<MachineSetting | null>(`/machines/settings/${exerciseId}`)
  }

  async function saveSetting(exerciseId: number, input: MachineSettingInput): Promise<MachineSetting> {
    return apiFetch<MachineSetting>(`/machines/settings/${exerciseId}`, {
      method: 'PUT',
      body: input,
    })
  }

  return { fetchMachineExercises, fetchSettings, fetchSetting, saveSetting }
}
