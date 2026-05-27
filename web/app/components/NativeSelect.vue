<template>
  <select
    :value="modelValue"
    class="border-default bg-elevated text-default w-full rounded-lg border px-3 py-2.5 text-base"
    @change="onChange"
  >
    <option v-if="placeholder" disabled value="">{{ placeholder }}</option>
    <option v-for="item in items" :key="String(item.value)" :value="item.value">
      {{ item.label }}
    </option>
  </select>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue'

interface SelectItem {
  label: string
  value: string | number
}

defineProps({
  modelValue: {
    type: [String, Number] as PropType<string | number | undefined>,
    default: undefined,
  },
  items: {
    type: Array as PropType<SelectItem[]>,
    required: true,
  },
  placeholder: {
    type: String,
    default: '',
  },
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

/**
 * Propage la valeur sélectionnée (select natif iOS).
 * @param event - Événement change.
 */
function onChange(event: Event): void {
  const target = event.target as HTMLSelectElement
  const raw = target.value
  const match = target.selectedOptions[0]
  const itemValue = match?.value ?? raw
  const numeric = Number(itemValue)
  emit('update:modelValue', Number.isNaN(numeric) || itemValue !== String(numeric) ? itemValue : numeric)
}
</script>
