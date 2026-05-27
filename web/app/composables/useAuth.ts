import type { Ref } from 'vue'
import type { TokenResponse, UserPublic } from '~/types/api'

/**
 * Gère l'état d'authentification : token persistant (cookie), profil utilisateur et actions.
 * @returns Les helpers d'authentification (login, register, logout, fetchMe) et l'état.
 */
export function useAuth(): {
  user: Ref<UserPublic | null>
  isAuthenticated: Ref<boolean>
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, displayName: string) => Promise<void>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
} {
  const token = useAuthToken()
  const user = useState<UserPublic | null>('fitdex_user', () => null)
  const isAuthenticated = computed<boolean>(() => Boolean(token.value))
  const { apiFetch } = useApi()

  /**
   * Récupère le profil de l'utilisateur connecté, ou réinitialise l'état si le token est invalide.
   */
  async function fetchMe(): Promise<void> {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      user.value = await apiFetch<UserPublic>('/auth/me')
    } catch {
      token.value = null
      user.value = null
    }
  }

  /**
   * Authentifie l'utilisateur et charge son profil.
   * @param email - Email.
   * @param password - Mot de passe.
   */
  async function login(email: string, password: string): Promise<void> {
    const res = await apiFetch<TokenResponse>('/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    token.value = res.access_token
    await fetchMe()
  }

  /**
   * Inscrit un nouvel utilisateur puis charge son profil.
   * @param email - Email.
   * @param password - Mot de passe (8 caractères minimum).
   * @param displayName - Nom affiché.
   */
  async function register(email: string, password: string, displayName: string): Promise<void> {
    const res = await apiFetch<TokenResponse>('/auth/register', {
      method: 'POST',
      body: { email, password, display_name: displayName },
    })
    token.value = res.access_token
    await fetchMe()
  }

  /**
   * Déconnecte l'utilisateur et le renvoie vers la page de connexion.
   */
  async function logout(): Promise<void> {
    token.value = null
    user.value = null
    await navigateTo('/login')
  }

  return { user, isAuthenticated, login, register, logout, fetchMe }
}
