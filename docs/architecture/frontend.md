# Frontend architecture

## Stack

Vue 3 (Composition API, `<script setup>`) · TypeScript (strict) · Vite · Vue Router · Pinia · Tailwind CSS · Axios · Vitest + Vue Test Utils · Playwright.

## Layout

```
frontend/src/
  api/        axios instance + auth.ts + tasks.ts clients (typed)
  components/ ui primitives (BaseButton, BaseInput, BaseCard, BaseModal,
              TaskStatusBadge, TaskPriorityBadge, AlertBanner, AppPagination)
  composables/ useAuth(), useTasks(), useDebouncedRef()
  layouts/    AppLayout (nav shell) · AuthLayout (centered card)
  pages/      LoginPage, RegisterPage, DashboardPage, TaskListPage,
              TaskCreatePage, TaskEditPage, TaskDetailPage, NotFoundPage
  router/     index.ts + auth guard (meta.requiresAuth)
  stores/     auth.ts (token + user + actions) · tasks.ts (list/filters/pagination)
  types/      domain types mirroring API contracts
  utils/      formatters (dates), validators
```

## Data flow

1. Components call composables/stores; stores call `src/api/*` clients.
2. `src/api/client.ts` creates a shared Axios instance with `VITE_API_BASE_URL` and an auth request interceptor.
3. Access token lives in memory (Pinia store); refresh token is kept in `localStorage` only for session persistence — a documented trade-off (see Security below). A response interceptor retries once with the refresh token on a 401, then forces logout.
4. Router guard redirects unauthenticated users of `meta.requiresAuth` pages to `/login`, preserving the intended target.

## Security trade-offs

- Tokens are not long-lived credentials; access tokens are short-lived and held in memory. Refresh persistence in `localStorage` is a pragmatic trade-off for a demo SPA; production deployments should prefer rotating refresh tokens server-side and consider cookie-based delivery. Do not store passwords anywhere.

## UI conventions

- Tailwind utility classes; responsive grids (`sm:`/`lg:` breakpoints); semantic HTML and labels for accessibility.
- Loading (skeletons/spinners), empty, and error states are mandatory for data pages.
- Destructive actions require a confirmation dialog.
- Status/priority badges are single reusable components, not ad-hoc styling.

## Testing

- Vitest + Vue Test Utils for components/stores/composables; Axios is mocked via `vi.mock('src/api/client')` or MSW-style handler stubs.
- Playwright specs in `frontend/tests/e2e/` cover register → login → CRUD flows and route protection.
