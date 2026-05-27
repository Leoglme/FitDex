import type { Ref } from 'vue'

/**
 * Source de vérité unique du token d'authentification.
 *
 * `useState` garantit une ref partagée entre tous les composables (contrairement à
 * `useCookie` dont chaque appel renvoie une ref indépendante non synchronisée). Le cookie
 * sert uniquement à la persistance : toute écriture du token y est répercutée.
 * @returns La ref réactive et partagée du token (`null` si non authentifié).
 */
export function useAuthToken(): Ref<string | null> {
  const cookie = useCookie<string | null>('fitdex_token', {
    maxAge: 60 * 60 * 24 * 30,
    sameSite: 'lax',
  })
  const token = useState<string | null>('fitdex_token', () => cookie.value)

  // Persiste toute mutation du token dans le cookie (source unique = useState).
  watch(token, (value: string | null): void => {
    cookie.value = value
  })

  return token
}
