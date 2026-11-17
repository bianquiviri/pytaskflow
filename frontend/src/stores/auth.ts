import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@/api/auth'

const REFRESH_KEY = 'taskflow.refresh'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<authApi.AuthResponse['user'] | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => accessToken.value !== null)

  function setSession(auth: authApi.AuthResponse): void {
    user.value = auth.user
    accessToken.value = auth.access
    refreshToken.value = auth.refresh
    if (auth.refresh) {
      localStorage.setItem(REFRESH_KEY, auth.refresh)
    } else {
      localStorage.removeItem(REFRESH_KEY)
    }
  }

  function clearSession(): void {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(payload: { email: string; password: string }): Promise<void> {
    setSession(await authApi.login(payload))
  }

  async function register(payload: {
    email: string
    password: string
    first_name: string
    last_name: string
  }): Promise<void> {
    setSession(await authApi.register(payload))
  }

  /** Exchange the stored refresh token for a fresh access token; null on failure. */
  async function refreshAccess(): Promise<string | null> {
    if (!refreshToken.value) return null
    try {
      const tokens = await authApi.refreshTokens(refreshToken.value)
      accessToken.value = tokens.access
      if (tokens.refresh) {
        refreshToken.value = tokens.refresh
        localStorage.setItem(REFRESH_KEY, tokens.refresh)
      }
      return tokens.access
    } catch {
      clearSession()
      return null
    }
  }

  /** Restore a session from the persisted refresh token at app start. */
  async function initialize(): Promise<void> {
    if (initialized.value) return
    initialized.value = true
    const stored = localStorage.getItem(REFRESH_KEY)
    if (!stored) return
    refreshToken.value = stored
    const access = await refreshAccess()
    if (access) {
      try {
        user.value = await authApi.fetchMe()
      } catch {
        clearSession()
      }
    }
  }

  async function logout(): Promise<void> {
    try {
      if (refreshToken.value) await authApi.logout(refreshToken.value)
    } finally {
      clearSession()
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    initialized,
    isAuthenticated,
    login,
    register,
    logout,
    refreshAccess,
    initialize,
    setSession,
    clearSession,
  }
})
