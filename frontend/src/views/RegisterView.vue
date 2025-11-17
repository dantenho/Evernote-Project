<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-green-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <div class="card">
        <div class="text-center mb-8">
          <h2 class="text-3xl font-bold text-gray-900">Create Your Account</h2>
          <p class="mt-2 text-gray-600">Start your learning journey today</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <div v-if="typeof error === 'string'">{{ error }}</div>
            <div v-else>
              <div v-for="(messages, field) in error" :key="field">
                <strong>{{ field }}:</strong> {{ Array.isArray(messages) ? messages.join(', ') : messages }}
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                First Name
              </label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                required
                class="input"
                placeholder="John"
              />
            </div>

            <div>
              <label for="last_name" class="block text-sm font-medium text-gray-700 mb-2">
                Last Name
              </label>
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                required
                class="input"
                placeholder="Doe"
              />
            </div>
          </div>

          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="input"
              placeholder="Choose a username"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input"
              placeholder="Create a strong password"
            />
          </div>

          <div>
            <label for="password2" class="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              id="password2"
              v-model="form.password2"
              type="password"
              required
              class="input"
              placeholder="Re-enter your password"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full btn btn-primary"
          >
            {{ loading ? 'Creating Account...' : 'Sign Up' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
              Sign in
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
})

const loading = ref(false)
const error = ref(null)

const handleSubmit = async () => {
  loading.value = true
  error.value = null

  const result = await authStore.register(form.value)

  if (result.success) {
    router.push('/dashboard')
  } else {
    error.value = result.error
  }

  loading.value = false
}
</script>
