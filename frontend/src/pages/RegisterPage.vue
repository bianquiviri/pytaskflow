<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AlertBanner from '@/components/AlertBanner.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import { errorMessage } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', password: '', first_name: '', last_name: '' })
const submitting = ref(false)
const error = ref<string | null>(null)
const fieldErrors = reactive<{ password?: string }>({})

function validate(): boolean {
  fieldErrors.password = undefined
  if (form.password.length < 8) fieldErrors.password = 'Password must be at least 8 characters.'
  return !fieldErrors.password
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  error.value = null
  try {
    await auth.register(form)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="rounded-lg bg-white p-6 shadow-sm">
    <h2 class="mb-4 text-lg font-semibold text-slate-900">Create account</h2>
    <AlertBanner type="error" :message="error" />
    <form novalidate @submit.prevent="submit">
      <BaseInput v-model="form.first_name" label="First name" autocomplete="given-name" />
      <BaseInput v-model="form.last_name" label="Last name" autocomplete="family-name" />
      <BaseInput v-model="form.email" label="Email" type="email" required autocomplete="email" />
      <BaseInput
        v-model="form.password"
        label="Password"
        type="password"
        required
        autocomplete="new-password"
        placeholder="Minimum 8 characters"
        :error="fieldErrors.password"
      />
      <BaseButton type="submit" class="w-full" :loading="submitting">Register</BaseButton>
    </form>
    <p class="mt-4 text-center text-sm text-slate-600">
      Already registered?
      <RouterLink to="/login" class="font-medium text-blue-600 hover:underline">Log in</RouterLink>
    </p>
  </div>
</template>
