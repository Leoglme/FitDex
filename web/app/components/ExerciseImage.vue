<template>
  <img
    v-if="src && !failed"
    :src="src"
    :alt="alt"
    :class="imgClass"
    loading="lazy"
    @error="failed = true"
  />
  <div v-else :class="['flex shrink-0 items-center justify-center rounded-lg bg-muted', placeholderClass]">
    <UIcon :name="equipmentIcon(equipment)" class="text-muted h-5 w-5" />
  </div>
</template>

<script lang="ts" setup>
import type { PropType } from 'vue'
import type { Equipment } from '~/types/api'
import { equipmentIcon } from '~/utils/equipment'
import { resolveMediaUrl } from '~/utils/mediaUrl'

const props = defineProps({
  imagePath: {
    type: String as PropType<string | null>,
    default: null,
  },
  equipment: {
    type: String as PropType<Equipment>,
    default: 'machine',
  },
  alt: {
    type: String,
    default: '',
  },
  imgClass: {
    type: String,
    default: 'h-14 w-14 shrink-0 rounded-lg object-contain bg-white/90 p-0.5',
  },
  placeholderClass: {
    type: String,
    default: 'h-12 w-12',
  },
})

const failed = ref(false)

const src = computed((): string | null => resolveMediaUrl(props.imagePath))

watch(
  (): string | null => props.imagePath,
  (): void => {
    failed.value = false
  },
)
</script>
