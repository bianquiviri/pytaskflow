import type { NavigationGuardWithThis } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Route guard for `meta.requiresAuth` routes.
 * Unauthenticated users are redirected to /login with the intended target
 * preserved as `?redirect=` so the login page can send them back afterwards.
 */
export const requireAuth: NavigationGuardWithThis<undefined> = async (to) => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    await auth.initialize()
  }
  if (!auth.isAuthenticated && to.meta.requiresAuth) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
}
