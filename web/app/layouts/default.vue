<template>
  <div class="bg-default text-default flex min-h-screen flex-col">
    <header class="border-default bg-default/80 sticky top-0 z-30 border-b backdrop-blur">
      <div class="mx-auto flex w-full max-w-3xl items-center justify-between px-4 py-3">
        <NuxtLink to="/" class="flex items-center gap-2">
          <FitDexLogo class="h-8 w-8" />
          <span class="text-lg font-extrabold tracking-tight">FitDex</span>
        </NuxtLink>
        <div v-if="isAuthenticated" class="flex items-center gap-2">
          <span class="text-muted hidden text-sm sm:inline">{{ user?.display_name }}</span>
          <UButton color="neutral" variant="ghost" icon="lucide:log-out" aria-label="Déconnexion" @click="logout" />
        </div>
      </div>
    </header>

    <main class="mx-auto w-full max-w-3xl flex-1 px-4 pt-4 pb-24">
      <slot />
    </main>

    <nav
      v-if="isAuthenticated"
      class="border-default bg-default/90 fixed inset-x-0 bottom-0 z-30 border-t backdrop-blur"
    >
      <div class="mx-auto grid w-full max-w-3xl grid-cols-4">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition-colors sm:text-xs"
          :class="isActive(item.to) ? 'text-primary' : 'text-muted'"
        >
          <UIcon :name="item.icon" class="h-6 w-6" />
          {{ item.label }}
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>

<script lang="ts" setup>
import type { ComputedRef } from 'vue'

interface NavItem {
  to: string
  label: string
  icon: string
}

const { user, isAuthenticated, logout } = useAuth()
const route = useRoute()

const navItems: NavItem[] = [
  { to: '/', label: 'Séances', icon: 'lucide:dumbbell' },
  { to: '/machines', label: 'Machines', icon: 'lucide:cog' },
  { to: '/stats', label: 'Stats', icon: 'lucide:trending-up' },
  { to: '/profil', label: 'Profil', icon: 'lucide:user' },
]

const currentPath: ComputedRef<string> = computed(() => route.path)

/**
 * Indique si l'onglet correspond à la route courante.
 * @param to - Chemin de l'onglet.
 * @returns `true` si l'onglet est actif.
 */
function isActive(to: string): boolean {
  if (to === '/') {
    return currentPath.value === '/' || currentPath.value.startsWith('/seances')
  }
  return currentPath.value.startsWith(to)
}
</script>
