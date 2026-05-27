/**
 * Middleware de route : renvoie l'utilisateur déjà connecté vers l'accueil.
 */
export default defineNuxtRouteMiddleware(() => {
  const token = useCookie<string | null>('fitdex_token')
  if (token.value) {
    return navigateTo('/')
  }
})
