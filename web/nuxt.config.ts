// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/eslint', '@nuxt/ui', '@vueuse/nuxt', '@vite-pwa/nuxt', '@nuxtjs/sitemap', '@nuxtjs/robots'],

  // Nom du composant = nom du fichier (ex : FitDexLogo), sans préfixe de dossier.
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],

  devtools: { enabled: true },

  css: ['~/assets/css/main.css'],

  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'https://fit.dibodev.fr',
    name: 'FitDex',
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:8010',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://fit.dibodev.fr',
    },
  },

  compatibilityDate: '2024-07-11',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs',
      },
    },
  },

  icon: {
    mode: 'svg',
  },

  pwa: {
    registerType: 'autoUpdate',
    includeAssets: ['favicon.svg', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'icon-512-maskable.png'],
    manifest: {
      name: 'FitDex',
      short_name: 'FitDex',
      description: 'Suivi de progression en musculation : charges, répétitions et stats.',
      lang: 'fr',
      theme_color: '#84cc16',
      background_color: '#0a0a0a',
      display: 'standalone',
      orientation: 'portrait',
      icons: [
        { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
        { src: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
        { src: '/icon-512-maskable.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,svg,png,jpg,ico,woff2}'],
      navigateFallback: '/',
    },
    client: {
      installPrompt: true,
    },
    devOptions: {
      enabled: false,
    },
  },

  robots: {
    groups: [
      {
        userAgent: '*',
        allow: ['/'],
        disallow: ['/dashboard', '/seances', '/stats', '/login', '/register'],
      },
    ],
  },

  sitemap: {
    includeAppSources: false,
    urls: ['/'],
  },
})
