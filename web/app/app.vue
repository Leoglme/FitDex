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
  title: 'FitDex',
  titleTemplate: '%s',
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover' },
    { name: 'apple-mobile-web-app-title', content: 'FitDex' },
    { name: 'apple-mobile-web-app-capable', content: 'yes' },
    { name: 'application-name', content: 'FitDex' },
  ],
  link: [{ rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
})

useSeoMeta({
  title: 'FitDex',
  description: 'Suis tes charges, tes répétitions et ta progression à la salle. Stats par muscle, séance et exercice.',
  ogTitle: 'FitDex',
  ogDescription: 'Suivi de progression en musculation : charges, répétitions et statistiques.',
  themeColor: '#84cc16',
})
</script>
