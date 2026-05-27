import type { $Fetch, FetchOptions } from 'ofetch'

/**
 * Fournit un client HTTP typé vers l'API FitDex, avec base URL et token Bearer injectés.
 * @returns Un objet exposant `apiFetch` pour appeler l'API.
 */
export function useApi(): { apiFetch: <T>(path: string, options?: FetchOptions) => Promise<T> } {
  const config = useRuntimeConfig()
  const token = useAuthToken()

  const client: $Fetch = $fetch.create({
    baseURL: config.public.apiBase,
    /**
     *
     */
    onRequest({ options }) {
      if (token.value) {
        options.headers.set('Authorization', `Bearer ${token.value}`)
      }
    },
  })

  /**
   * Effectue un appel typé vers l'API.
   * @param path - Chemin relatif (ex: `/auth/me`).
   * @param options - Options ofetch (méthode, body, query…).
   * @returns La réponse désérialisée.
   */
  async function apiFetch<T>(path: string, options?: FetchOptions): Promise<T> {
    return client<T>(path, options as FetchOptions<'json'>)
  }

  return { apiFetch }
}
