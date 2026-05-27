/**
 * Middleware de route : redirige vers /login si l'utilisateur n'est pas authentifié.
 */
export default defineNuxtRouteMiddleware((to) => {
  const token = useCookie<string | null>('fitdex_token')
  if (!token.value) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }
})
