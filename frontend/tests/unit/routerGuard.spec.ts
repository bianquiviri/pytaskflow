import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { router } from '@/router'
import { useAuthStore } from '@/stores/auth'

const authApi = vi.hoisted(() => ({
  register: vi.fn(),
  login: vi.fn(),
  refreshTokens: vi.fn(),
  logout: vi.fn(),
  fetchMe: vi.fn(),
}))
vi.mock('@/api/auth', () => authApi)

const sessionUser = {
  id: 'u1',
  email: 'a@b.c',
  first_name: '',
  last_name: '',
  full_name: '',
  is_active: true,
  created_at: '',
  updated_at: '',
}

describe('app router auth guard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
    return router.push('/')
  })

  it('redirects unauthenticated users from protected routes to login', async () => {
    await router.push('/tasks')
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/tasks')
  })

  it('lets authenticated users reach protected routes', async () => {
    const auth = useAuthStore()
    auth.setSession({ user: sessionUser, access: 'access-token', refresh: 'refresh-token' })
    await router.push('/tasks')
    expect(router.currentRoute.value.name).toBe('task-list')
  })

  it('initialize() restores a session from the persisted refresh token', async () => {
    authApi.refreshTokens.mockResolvedValue({ access: 'a3', refresh: 'r3' })
    authApi.fetchMe.mockResolvedValue(sessionUser)
    localStorage.setItem('taskflow.refresh', 'stored')
    // Fresh pinia/store: app start-up path (the suite's store was already
    // initialized by the beforeEach navigation).
    setActivePinia(createPinia())
    const auth = useAuthStore()
    await auth.initialize()
    expect(auth.isAuthenticated).toBe(true)
    await router.push('/tasks')
    expect(router.currentRoute.value.name).toBe('task-list')
  })

  it('auth pages are reachable without a session', async () => {
    await router.push('/register')
    expect(router.currentRoute.value.name).toBe('register')
  })
})
