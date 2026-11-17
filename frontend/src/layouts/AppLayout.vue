<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/BaseButton.vue'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <RouterLink to="/" class="text-lg font-bold text-slate-900">TaskFlow</RouterLink>
        <nav class="flex items-center gap-4">
          <RouterLink to="/" class="text-sm text-slate-600 hover:text-slate-900">Dashboard</RouterLink>
          <RouterLink to="/tasks" class="text-sm text-slate-600 hover:text-slate-900">Tasks</RouterLink>
          <BaseButton variant="secondary" size="sm" @click="handleLogout">Log out</BaseButton>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
