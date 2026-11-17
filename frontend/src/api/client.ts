import axios, { type AxiosError, type AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

/** Shared Axios instance with JWT bearer interceptor + one-shot refresh retry. */
export const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

let refreshing: Promise<string | null> | null = null

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const auth = useAuthStore()
    const original = error.config as (typeof error.config & { _retry?: boolean }) | undefined
    if (error.response?.status === 401 && original && !original._retry && auth.refreshToken) {
      original._retry = true
      refreshing = refreshing ?? auth.refreshAccess()
      const access = await refreshing
      refreshing = null
      if (access) {
        original.headers.Authorization = `Bearer ${access}`
        return http(original)
      }
      auth.logout()
    }
    return Promise.reject(error)
  },
)

/** Extract DRF-style error messages from an Axios error. */
export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | string | undefined
    if (typeof data === 'string') return data
    if (data && typeof data === 'object') {
      const detail = data.detail
      if (typeof detail === 'string') return detail
      const firstField = Object.values(data)[0]
      if (Array.isArray(firstField) && firstField.length > 0) return String(firstField[0])
    }
    return error.message
  }
  return 'Unexpected error'
}
