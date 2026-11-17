<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AlertBanner from '@/components/AlertBanner.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import { errorMessage } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({ email: '', password: '' })
const submitting = ref(false)
const error = ref<string | null>(null)

async function submit() {
  submitting.value = true
  error.value = null
  try {
    await auth.login(form)
    router.push((route.query.redirect as string) ?? { name: 'dashboard' })
  } catch (e) {
    error.value = errorMessage(e) === 'Request failed with status code 401' ? 'Invalid email or password.' : errorMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="rounded-lg bg-white p-6 shadow-sm">
    <h2 class="mb-4 text-lg font-semibold text-slate-900">Log in</h2>
    <AlertBanner type="error" :message="error" />
    <form novalidate @submit.prevent="submit">
      <BaseInput v-model="form.email" label="Email" type="email" required autocomplete="email" />
      <BaseInput v-model="form.password" label="Password" type="password" required autocomplete="current-password" />
      <BaseButton type="submit" class="w-full" :loading="submitting">Log in</BaseButton>
    </form>
    <p class="mt-4 text-center text-sm text-slate-600">
      No account?
      <RouterLink to="/register" class="font-medium text-blue-600 hover:underline">Register</RouterLink>
    </p>
  </div>
</template>
