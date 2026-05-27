<template>
  <UApp>
    <NuxtRouteAnnouncer />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>

<script lang="ts" setup>
useHead({
  htmlAttrs: { lang: 'fr' },
  link: [{ rel: 'apple-touch-icon', href: '/icon-192.png' }],
})

useSeoMeta({
  title: 'FitDex — Suivi de progression en musculation',
  description: 'Suis tes charges, tes répétitions et ta progression à la salle. Stats par muscle, séance et exercice.',
  ogTitle: 'FitDex',
  ogDescription: 'Suivi de progression en musculation : charges, répétitions et statistiques.',
  themeColor: '#84cc16',
})
</script>
