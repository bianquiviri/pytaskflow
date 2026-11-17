import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '@/stores/auth'

const authApi = vi.hoisted(() => ({
  register: vi.fn(),
  login: vi.fn(),
  refreshTokens: vi.fn(),
  logout: vi.fn(),
  fetchMe: vi.fn(),
}))

vi.mock('@/api/auth', () => authApi)

const sampleUser = { id: 'u1', email: 'ada@example.test', first_name: 'Ada', last_name: 'L', full_name: 'Ada L', is_active: true, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' }
const tokens = { user: sampleUser, access: 'access-1', refresh: 'refresh-1' }

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('login stores tokens, user and persists refresh', async () => {
    authApi.login.mockResolvedValue(tokens)
    const auth = useAuthStore()
    await auth.login({ email: 'ada@example.test', password: 'pw' })
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.user?.email).toBe('ada@example.test')
    expect(localStorage.getItem('taskflow.refresh')).toBe('refresh-1')
  })

  it('logout clears the session and removes persisted refresh', async () => {
    authApi.login.mockResolvedValue(tokens)
    const auth = useAuthStore()
    await auth.login({ email: 'ada@example.test', password: 'pw' })
    await auth.logout()
    expect(auth.isAuthenticated).toBe(false)
    expect(auth.accessToken).toBeNull()
    expect(localStorage.getItem('taskflow.refresh')).toBeNull()
    expect(authApi.logout).toHaveBeenCalledWith('refresh-1')
  })

  it('refreshAccess updates the access token', async () => {
    authApi.login.mockResolvedValue(tokens)
    authApi.refreshTokens.mockResolvedValue({ access: 'access-2', refresh: 'refresh-2' })
    const auth = useAuthStore()
    await auth.login({ email: 'x@y.z', password: 'pw' })
    const access = await auth.refreshAccess()
    expect(access).toBe('access-2')
    expect(auth.refreshToken).toBe('refresh-2')
  })

  it('refresh failure clears the session', async () => {
    authApi.login.mockResolvedValue(tokens)
    authApi.refreshTokens.mockRejectedValue(new Error('expired'))
    const auth = useAuthStore()
    await auth.login({ email: 'x@y.z', password: 'pw' })
    const access = await auth.refreshAccess()
    expect(access).toBeNull()
    expect(auth.isAuthenticated).toBe(false)
  })

  it('initialize restores a session from persisted refresh token', async () => {
    authApi.refreshTokens.mockResolvedValue({ access: 'access-3', refresh: 'refresh-3' })
    authApi.fetchMe.mockResolvedValue(sampleUser)
    localStorage.setItem('taskflow.refresh', 'stored-refresh')
    const auth = useAuthStore()
    await auth.initialize()
    expect(auth.isAuthenticated).toBe(true)
    expect(auth.accessToken).toBe('access-3')
    expect(auth.user?.email).toBe('ada@example.test')
  })

  it('register delegates to the API and sets the session', async () => {
    authApi.register.mockResolvedValue(tokens)
    const auth = useAuthStore()
    await auth.register({ email: 'new@x.y', password: 'pw123456', first_name: 'A', last_name: 'B' })
    expect(auth.isAuthenticated).toBe(true)
  })
})
