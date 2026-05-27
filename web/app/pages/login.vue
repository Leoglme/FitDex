<template>
  <div class="mx-auto flex max-w-sm flex-col items-center pt-10">
    <FitDexLogo class="h-16 w-16" />
    <h1 class="mt-4 text-2xl font-extrabold">Connexion</h1>
    <p class="text-muted mt-1 text-center text-sm">Reprends ta progression là où tu l'as laissée.</p>

    <form class="mt-8 flex w-full flex-col gap-4" @submit.prevent="onSubmit">
      <UFormField label="Email">
        <UInput
          v-model="email"
          type="email"
          size="lg"
          placeholder="toi@exemple.fr"
          autocomplete="email"
          class="w-full"
        />
      </UFormField>
      <UFormField label="Mot de passe">
        <UInput
          v-model="password"
          type="password"
          size="lg"
          placeholder="••••••••"
          autocomplete="current-password"
          class="w-full"
        />
      </UFormField>
      <UButton type="submit" color="primary" size="lg" block :loading="loading">Se connecter</UButton>
    </form>

    <p class="text-muted mt-6 text-sm">
      Pas encore de compte ?
      <NuxtLink to="/register" class="text-primary font-semibold">Créer un espace</NuxtLink>
    </p>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import { FetchError } from 'ofetch'

definePageMeta({ middleware: 'guest', layout: 'default' })

const { login } = useAuth()
const route = useRoute()
const toast = useToast()

const email: Ref<string> = ref('')
const password: Ref<string> = ref('')
const loading: Ref<boolean> = ref(false)

/**
 * Soumet le formulaire de connexion et redirige vers la cible demandée.
 */
async function onSubmit(): Promise<void> {
  loading.value = true
  try {
    await login(email.value.trim(), password.value)
    const redirect: string = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await navigateTo(redirect)
  } catch (error) {
    const message: string =
      error instanceof FetchError && error.status === 401
        ? 'Email ou mot de passe incorrect.'
        : 'Connexion impossible. Réessaie.'
    toast.add({ title: message, color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>
