<template>
  <UApp>
    <div class="flex min-h-screen flex-col items-center justify-center gap-6 p-6 text-center">
      <FitDexLogo class="h-16 w-16" />
      <div>
        <h1 class="text-2xl font-extrabold">{{ error.statusCode }}</h1>
        <p class="text-muted mt-2">{{ message }}</p>
      </div>
      <UButton color="primary" size="lg" @click="handleClear">Retour à l'accueil</UButton>
    </div>
  </UApp>
</template>

<script lang="ts" setup>
import type { NuxtError } from '#app'
import type { ComputedRef } from 'vue'

const props = defineProps<{ error: NuxtError }>()

const message: ComputedRef<string> = computed(
  () => props.error.message || 'Une erreur est survenue. Réessaie dans un instant.',
)

/**
 * Réinitialise l'erreur et renvoie l'utilisateur vers l'accueil.
 */
function handleClear(): void {
  clearError({ redirect: '/' })
}
</script>
