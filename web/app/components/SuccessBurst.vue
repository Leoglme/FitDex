<template>
  <Transition name="fitdex-fade">
    <div
      v-if="props.show"
      class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/70 backdrop-blur-sm"
      role="alertdialog"
      aria-live="assertive"
      @click="emit('close')"
    >
      <div ref="burstRoot" class="relative flex flex-col items-center gap-5 px-6 text-center">
        <div class="relative">
          <span class="fitdex-success-ring absolute inset-0 rounded-full" />
          <div
            class="fitdex-success-pop fitdex-success-glow bg-primary flex h-28 w-28 items-center justify-center rounded-full text-black"
          >
            <UIcon name="lucide:check" class="h-16 w-16" />
          </div>
          <div ref="confetti" class="pointer-events-none absolute inset-0" />
        </div>
        <div class="fitdex-success-pop">
          <h2 class="text-3xl font-extrabold text-white">{{ props.title }}</h2>
          <p class="text-primary-300 mt-1 text-lg">{{ props.subtitle }}</p>
        </div>
        <UButton color="primary" size="xl" class="mt-2" @click="emit('close')">Continuer</UButton>
      </div>
    </div>
  </Transition>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import gsap from 'gsap'
import type { SuccessBurstProps } from '~/types/SuccessBurst'

/**
 * Définit les props du composant SuccessBurst.
 */
const props: SuccessBurstProps = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'Séance terminée !',
  },
  subtitle: {
    type: String,
    default: 'Bien joué, continue comme ça 💪',
  },
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

const confetti: Ref<HTMLElement | null> = ref(null)
const burstRoot: Ref<HTMLElement | null> = ref(null)

const PARTICLE_COUNT: number = 28
const PARTICLE_COLORS: string[] = ['#bef264', '#84cc16', '#a3e635', '#10b981', '#facc15']

/**
 * Génère une explosion de particules colorées via une timeline GSAP.
 */
function playConfetti(): void {
  const container: HTMLElement | null = confetti.value
  if (!container) {
    return
  }
  container.innerHTML = ''
  const prefersReduced: boolean =
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReduced) {
    return
  }
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const dot: HTMLDivElement = document.createElement('div')
    dot.style.position = 'absolute'
    dot.style.left = '50%'
    dot.style.top = '50%'
    dot.style.width = '10px'
    dot.style.height = '10px'
    dot.style.borderRadius = '2px'
    dot.style.backgroundColor = PARTICLE_COLORS[i % PARTICLE_COLORS.length] ?? '#84cc16'
    container.appendChild(dot)

    const angle: number = (Math.PI * 2 * i) / PARTICLE_COUNT + Math.random() * 0.4
    const distance: number = 90 + Math.random() * 90
    gsap.fromTo(
      dot,
      { x: 0, y: 0, opacity: 1, scale: 1, rotate: 0 },
      {
        x: Math.cos(angle) * distance,
        y: Math.sin(angle) * distance + 40,
        opacity: 0,
        scale: 0.3,
        rotate: Math.random() * 360,
        duration: 1 + Math.random() * 0.5,
        ease: 'power2.out',
      },
    )
  }
}

watch(
  () => props.show,
  (visible: boolean): void => {
    if (visible) {
      void nextTick(() => playConfetti())
    }
  },
)
</script>

<style scoped>
.fitdex-fade-enter-active,
.fitdex-fade-leave-active {
  transition: opacity 0.25s ease;
}

.fitdex-fade-enter-from,
.fitdex-fade-leave-to {
  opacity: 0;
}
</style>
