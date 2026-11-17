import { expect, test } from '@playwright/test'
import { registerThroughUi, uniqueUser } from './helpers'

const TASK_TITLE = 'E2E smoke task'
const UPDATED_TITLE = 'E2E smoke task (edited)'

test('create, edit, change status and delete a task', async ({ page }) => {
  await registerThroughUi(page, uniqueUser('tasks'))

  // Create
  await page.getByRole('link', { name: 'Tasks' }).click()
  await page.getByRole('link', { name: 'New task' }).click()
  await page.getByLabel('Title').fill(TASK_TITLE)
  await page.getByLabel('Description').fill('Created by the E2E suite')
  await page.getByLabel('Priority').selectOption('high')
  await page.getByRole('button', { name: 'Create task' }).click()

  // Detail view shows the created task
  await expect(page.getByRole('heading', { name: TASK_TITLE })).toBeVisible({ timeout: 10_000 })

  // Edit title
  await page.getByRole('link', { name: 'Edit' }).click()
  await page.getByLabel('Title').fill(UPDATED_TITLE)
  await page.getByRole('button', { name: 'Save changes' }).click()
  await expect(page.getByRole('heading', { name: UPDATED_TITLE })).toBeVisible({ timeout: 10_000 })

  // Change status to in progress; the current status button becomes disabled
  await page.getByRole('button', { name: 'in progress' }).click()
  await expect(page.getByRole('button', { name: 'in progress' })).toBeDisabled({ timeout: 10_000 })

  // Delete with confirmation
  await page.getByRole('button', { name: 'Delete' }).click()
  await expect(page.getByText('This action cannot be undone.')).toBeVisible()
  await page.getByRole('button', { name: 'Confirm' }).click()

  // Back on the list, empty state visible
  await expect(page.getByText('No tasks found')).toBeVisible({ timeout: 10_000 })
})
