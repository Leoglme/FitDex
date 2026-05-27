/**
 * Plugin client : charge le profil utilisateur au démarrage si un token est présent.
 */
export default defineNuxtPlugin(async () => {
  const { fetchMe } = useAuth()
  await fetchMe()
})
