import { defineConfig, devices } from '@playwright/test'

/**
 * E2E configuration.
 * Expects the stack running:
 *   docker compose up -d --build  (backend :8000, frontend :5173 or FRONTEND_PORT)
 * Override the frontend URL with E2E_BASE_URL and the API with E2E_API_URL.
 */
const baseURL = process.env.E2E_BASE_URL ?? 'http://localhost:5173'
const apiURL = process.env.E2E_API_URL ?? 'http://localhost:8000'

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [['html', { outputFolder: 'playwright-report', open: 'never' }], ['list']] : 'list',
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  metadata: { apiURL },
})
