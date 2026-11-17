import { createRouter, createWebHistory } from 'vue-router'
import { requireAuth } from '@/composables/useAuthGuard'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
        { path: 'tasks', name: 'task-list', component: () => import('@/pages/TaskListPage.vue') },
        { path: 'tasks/new', name: 'task-create', component: () => import('@/pages/TaskCreatePage.vue') },
        { path: 'tasks/:id', name: 'task-detail', component: () => import('@/pages/TaskDetailPage.vue') },
        { path: 'tasks/:id/edit', name: 'task-edit', component: () => import('@/pages/TaskEditPage.vue') },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: 'login', name: 'login', component: () => import('@/pages/LoginPage.vue') },
        { path: 'register', name: 'register', component: () => import('@/pages/RegisterPage.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/NotFoundPage.vue') },
  ],
})

router.beforeEach(requireAuth)
