<template>
  <div class="mx-auto flex max-w-sm flex-col items-center pt-10">
    <FitDexLogo class="h-16 w-16" />
    <h1 class="mt-4 text-2xl font-extrabold">Créer ton espace</h1>
    <p class="text-muted mt-1 text-center text-sm">Ton suivi de progression, rien qu'à toi.</p>

    <form class="mt-8 flex w-full flex-col gap-4" @submit.prevent="onSubmit">
      <UFormField label="Prénom / pseudo">
        <UInput v-model="displayName" size="lg" placeholder="Léo" autocomplete="nickname" class="w-full" />
      </UFormField>
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
      <UFormField label="Mot de passe" help="8 caractères minimum">
        <UInput
          v-model="password"
          type="password"
          size="lg"
          placeholder="••••••••"
          autocomplete="new-password"
          class="w-full"
        />
      </UFormField>
      <UButton type="submit" color="primary" size="lg" block :loading="loading">Créer mon compte</UButton>
    </form>

    <p class="text-muted mt-6 text-sm">
      Déjà un compte ?
      <NuxtLink to="/login" class="text-primary font-semibold">Se connecter</NuxtLink>
    </p>
  </div>
</template>

<script lang="ts" setup>
import type { Ref } from 'vue'
import { FetchError } from 'ofetch'

definePageMeta({ middleware: 'guest', layout: 'default' })

const { register } = useAuth()
const toast = useToast()

const displayName: Ref<string> = ref('')
const email: Ref<string> = ref('')
const password: Ref<string> = ref('')
const loading: Ref<boolean> = ref(false)

/**
 * Valide la saisie puis inscrit l'utilisateur et le redirige vers l'accueil.
 */
async function onSubmit(): Promise<void> {
  if (password.value.length < 8) {
    toast.add({ title: 'Le mot de passe doit faire au moins 8 caractères.', color: 'error' })
    return
  }
  if (!displayName.value.trim()) {
    toast.add({ title: 'Indique un prénom ou un pseudo.', color: 'error' })
    return
  }
  loading.value = true
  try {
    await register(email.value.trim(), password.value, displayName.value.trim())
    await navigateTo('/')
  } catch (error) {
    const message: string =
      error instanceof FetchError && error.status === 409
        ? 'Cet email est déjà utilisé.'
        : 'Inscription impossible. Réessaie.'
    toast.add({ title: message, color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>
