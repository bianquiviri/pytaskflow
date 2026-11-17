import { expect, test } from '@playwright/test'
import { loginThroughUi, registerThroughUi, uniqueUser } from './helpers'

test('a new user can register and lands on the dashboard', async ({ page }) => {
  const user = uniqueUser('register')
  await registerThroughUi(page, user)
  await expect(page.getByText('Total tasks')).toBeVisible()
})

test('a registered user can log in and log out', async ({ page }) => {
  const user = uniqueUser('login')
  await registerThroughUi(page, user)
  await page.getByRole('button', { name: 'Log out' }).click()
  await expect(page).toHaveURL(/\/login$/)

  await loginThroughUi(page, user)
  await expect(page.getByText('Total tasks')).toBeVisible()
})

test('wrong credentials are rejected with a visible error', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill('nobody@nowhere.test')
  await page.getByLabel('Password').fill('wrong-password-1')
  await page.getByRole('button', { name: 'Log in' }).click()
  await expect(page.getByRole('alert')).toBeVisible({ timeout: 10_000 })
})
