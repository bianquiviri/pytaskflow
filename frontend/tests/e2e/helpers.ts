import { type APIRequestContext, type Page, expect } from '@playwright/test'

const API = process.env.E2E_API_URL ?? 'http://localhost:8000'

export interface TestUser {
  email: string
  password: string
  first_name: string
  last_name: string
}

/** Unique user per test run to avoid collisions between runs. */
export function uniqueUser(prefix: string): TestUser {
  return {
    email: `${prefix}.${Date.now()}-${Math.floor(Math.random() * 10_000)}@e2e.taskflow.local`,
    password: 'S3cure-e2e-password!',
    first_name: 'E2E',
    last_name: prefix.charAt(0).toUpperCase() + prefix.slice(1),
  }
}

export async function registerViaApi(request: APIRequestContext, user: TestUser): Promise<void> {
  const response = await request.post(`${API}/api/v1/auth/register/`, { data: user })
  expect(response.ok(), `registration via API failed: ${await response.text()}`).toBeTruthy()
}

/** Register through the UI (used by the registration scenario itself). */
export async function registerThroughUi(page: Page, user: TestUser): Promise<void> {
  await page.goto('/register')
  await page.getByLabel('First name').fill(user.first_name)
  await page.getByLabel('Last name').fill(user.last_name)
  await page.getByLabel('Email').fill(user.email)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Register' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 10_000 })
}

export async function loginThroughUi(page: Page, user: TestUser): Promise<void> {
  await page.goto('/login')
  await page.getByLabel('Email').fill(user.email)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Log in' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible({ timeout: 10_000 })
}
