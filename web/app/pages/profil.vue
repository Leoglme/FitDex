<template>
  <div>
    <h1 class="text-2xl font-extrabold">Profil</h1>

    <div class="border-default bg-elevated/40 mt-6 flex flex-col gap-4 rounded-xl border p-5">
      <div class="flex items-center gap-3">
        <div
          class="bg-primary flex h-12 w-12 items-center justify-center rounded-full text-xl font-extrabold text-black"
        >
          {{ initial }}
        </div>
        <div>
          <p class="font-bold">{{ user?.display_name }}</p>
          <p class="text-muted text-sm">{{ user?.email }}</p>
        </div>
      </div>
    </div>

    <UButton class="mt-6" color="error" variant="subtle" size="lg" block icon="lucide:log-out" @click="logout">
      Se déconnecter
    </UButton>
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef } from 'vue'

definePageMeta({ middleware: 'auth' })

const { user, logout } = useAuth()

const initial: ComputedRef<string> = computed(() => (user.value?.display_name ?? '?').charAt(0).toUpperCase())
</script>
