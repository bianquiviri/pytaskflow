import { expect, test } from '@playwright/test'
import { uniqueUser } from './helpers'

test('unauthenticated users are redirected to login from protected pages', async ({ page }) => {
  await page.goto('/tasks')
  await expect(page).toHaveURL(/\/login\?redirect=\/tasks$/)
  await expect(page.getByRole('heading', { name: 'Log in' })).toBeVisible()
})

test('dashboard requires authentication too', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveURL(/\/login/)
})

test('login preserves the intended target after redirect', async ({ page }) => {
  const user = uniqueUser('guard')
  // Register via the UI first (gets us a session), then log out.
  await page.goto('/register')
  await page.getByLabel('First name').fill(user.first_name)
  await page.getByLabel('Last name').fill(user.last_name)
  await page.getByLabel('Email').fill(user.email)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Register' }).click()
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  await page.getByRole('button', { name: 'Log out' }).click()
  await expect(page).toHaveURL(/\/login$/)

  // Visiting /tasks while logged out then logging in should return to /tasks.
  await page.goto('/tasks')
  await expect(page).toHaveURL(/\/login\?redirect=\/tasks$/)
  await page.getByLabel('Email').fill(user.email)
  await page.getByLabel('Password').fill(user.password)
  await page.getByRole('button', { name: 'Log in' }).click()
  await expect(page).toHaveURL(/\/tasks$/, { timeout: 10_000 })
})
