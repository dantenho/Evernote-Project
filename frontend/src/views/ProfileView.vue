<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">My Profile</h1>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-600">Loading profile...</div>
      </div>

      <!-- Profile Content -->
      <div v-else class="space-y-6">
        <!-- Profile Information -->
        <div class="card bg-white">
          <h2 class="text-xl font-bold text-gray-900 mb-6">Profile Information</h2>

          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <div v-if="typeof error === 'string'">{{ error }}</div>
              <div v-else>
                <div v-for="(messages, field) in error" :key="field">
                  <strong>{{ field }}:</strong> {{ Array.isArray(messages) ? messages.join(', ') : messages }}
                </div>
              </div>
            </div>

            <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              {{ success }}
            </div>

            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                id="username"
                v-model="authStore.user.username"
                type="text"
                disabled
                class="input bg-gray-100 cursor-not-allowed"
              />
              <p class="mt-1 text-sm text-gray-500">Username cannot be changed</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="first_name" class="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  id="first_name"
                  v-model="form.first_name"
                  type="text"
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
                  class="input"
                  placeholder="Doe"
                />
              </div>
            </div>

            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="input"
                placeholder="your.email@example.com"
              />
            </div>

            <div class="flex items-center space-x-4">
              <button
                type="submit"
                :disabled="saving"
                class="btn btn-primary"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>

              <button
                type="button"
                @click="resetForm"
                class="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        <!-- Account Actions -->
        <div class="card bg-white">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Account Actions</h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div>
                <h3 class="font-medium text-gray-900">Sign Out</h3>
                <p class="text-sm text-gray-600">Sign out of your account on this device</p>
              </div>
              <button
                @click="handleLogout"
                class="btn btn-secondary"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>

        <!-- Account Stats (Optional) -->
        <div class="card bg-gradient-to-br from-primary-50 to-green-100">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Your Learning Journey</h2>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <div class="text-2xl font-bold text-primary-700">
                {{ authStore.user.date_joined ? daysSinceJoined : 0 }}
              </div>
              <div class="text-sm text-gray-600">Days Active</div>
            </div>

            <div class="text-center">
              <div class="text-2xl font-bold text-primary-700">-</div>
              <div class="text-sm text-gray-600">Total XP</div>
            </div>

            <div class="text-center">
              <div class="text-2xl font-bold text-primary-700">-</div>
              <div class="text-sm text-gray-600">Streak</div>
            </div>

            <div class="text-center">
              <div class="text-2xl font-bold text-primary-700">-</div>
              <div class="text-sm text-gray-600">Achievements</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const success = ref(null)

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
})

const daysSinceJoined = computed(() => {
  if (!authStore.user?.date_joined) return 0

  const joinDate = new Date(authStore.user.date_joined)
  const now = new Date()
  const diffMs = now - joinDate
  return Math.floor(diffMs / (1000 * 60 * 60 * 24))
})

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch fresh profile data
    await authStore.fetchProfile()

    // Initialize form with current data
    resetForm()
  } catch (err) {
    error.value = 'Failed to load profile. Please try again.'
    console.error('Profile load error:', err)
  } finally {
    loading.value = false
  }
})

const resetForm = () => {
  form.value = {
    first_name: authStore.user?.first_name || '',
    last_name: authStore.user?.last_name || '',
    email: authStore.user?.email || '',
  }
  error.value = null
  success.value = null
}

const handleSubmit = async () => {
  saving.value = true
  error.value = null
  success.value = null

  const result = await authStore.updateProfile(form.value)

  if (result.success) {
    success.value = 'Profile updated successfully!'
    setTimeout(() => {
      success.value = null
    }, 3000)
  } else {
    error.value = result.error || 'Failed to update profile. Please try again.'
  }

  saving.value = false
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
