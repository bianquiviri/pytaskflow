import type { AuthTokens, User } from '@/types'
import { http } from './client'

export interface AuthResponse {
  user: User
  access: string
  refresh: string
}

export async function register(payload: {
  email: string
  password: string
  first_name: string
  last_name: string
}): Promise<AuthResponse> {
  const { data } = await http.post<AuthResponse>('/auth/register/', payload)
  return data
}

export async function login(payload: { email: string; password: string }): Promise<AuthResponse> {
  const { data } = await http.post<AuthResponse>('/auth/login/', payload)
  return data
}

export async function refreshTokens(refresh: string): Promise<AuthTokens> {
  const { data } = await http.post<AuthTokens>('/auth/refresh/', { refresh })
  return data
}

export async function logout(refresh: string): Promise<void> {
  await http.post('/auth/logout/', { refresh })
}

export async function fetchMe(): Promise<User> {
  const { data } = await http.get<User>('/auth/me/')
  return data
}
