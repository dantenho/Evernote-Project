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

        <!-- Account Stats -->
        <div class="card bg-gradient-to-br from-primary-50 via-purple-50 to-pink-50 animate-fade-in">
          <h2 class="text-xl font-bold text-gray-900 mb-6">🎯 Your Learning Journey</h2>

          <!-- Rank Display Banner -->
          <div v-if="authStore.user?.profile" class="mb-6 p-6 bg-white rounded-xl shadow-md border-2 animate-scale-in" :style="{ borderColor: authStore.user.profile.rank_color || '#3B82F6' }">
            <div class="flex items-center justify-between flex-wrap gap-4">
              <!-- Rank Info -->
              <div class="flex items-center space-x-4">
                <div class="text-5xl animate-bounce-subtle">
                  {{ authStore.user.profile.rank_icon || '🏆' }}
                </div>
                <div>
                  <div class="text-sm text-gray-600 mb-1">Current Rank</div>
                  <div class="text-3xl font-bold" :style="{ color: authStore.user.profile.rank_color || '#000' }">
                    {{ authStore.user.profile.rank_name || 'Latão' }}
                  </div>
                  <div class="text-sm text-gray-500 mt-1">
                    {{ authStore.user.profile.xp_points }} XP Total
                  </div>
                </div>
              </div>

              <!-- Streak Display -->
              <div class="text-center px-6 py-3 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
                <div class="flex items-center justify-center space-x-2 mb-1">
                  <span class="text-3xl animate-flicker">🔥</span>
                  <span class="text-3xl font-bold text-orange-600">
                    {{ authStore.user.profile.current_streak || 0 }}
                  </span>
                </div>
                <div class="text-xs text-gray-600">Day Streak</div>
                <div v-if="authStore.user.profile.longest_streak > 0" class="text-xs text-gray-500 mt-1">
                  Best: {{ authStore.user.profile.longest_streak }} days
                </div>
              </div>
            </div>

            <!-- Rank Progress Bar -->
            <div class="mt-6">
              <div class="flex items-center justify-between text-sm text-gray-700 mb-2">
                <span class="font-semibold">Progress to {{ authStore.user.profile.next_rank_name || 'Max Rank' }}</span>
                <span class="font-semibold">
                  {{ authStore.user.profile.xp_in_current_rank || 0 }} / {{ authStore.user.profile.xp_for_next_rank || 100 }} XP
                </span>
              </div>
              <div class="w-full h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                <div
                  class="h-full rounded-full transition-all duration-700 ease-out animate-pulse-subtle"
                  :style="{
                    width: `${authStore.user.profile.progress_to_next_rank || 0}%`,
                    background: `linear-gradient(90deg, ${authStore.user.profile.rank_color || '#3B82F6'}, ${authStore.user.profile.rank_color || '#8B5CF6'})`
                  }"
                ></div>
              </div>
              <div class="text-xs text-gray-500 mt-1 text-right">
                {{ Math.round(authStore.user.profile.progress_to_next_rank || 0) }}% complete
              </div>
            </div>
          </div>

          <!-- Quick Stats Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.1s">
              <div class="text-2xl font-bold text-primary-700">
                {{ authStore.user.date_joined ? daysSinceJoined : 0 }}
              </div>
              <div class="text-sm text-gray-600">Days Active</div>
            </div>

            <div class="text-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.2s">
              <div class="text-2xl font-bold text-purple-700">
                {{ authStore.user?.profile?.xp_points || 0 }}
              </div>
              <div class="text-sm text-gray-600">Total XP</div>
            </div>

            <div class="text-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.3s">
              <div class="text-2xl font-bold" :style="{ color: authStore.user?.profile?.rank_color || '#16A34A' }">
                {{ authStore.user?.profile?.rank_icon || '🏆' }} Tier {{ authStore.user?.profile?.rank_tier || 0 }}
              </div>
              <div class="text-sm text-gray-600">Rank Tier</div>
            </div>

            <div class="text-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.4s">
              <div class="text-2xl font-bold text-orange-700">
                🏆 {{ achievementsCount }}
              </div>
              <div class="text-sm text-gray-600">Achievements</div>
            </div>
          </div>
        </div>

        <!-- Achievements Section -->
        <AchievementsList ref="achievementsListRef" @achievements-loaded="updateAchievementsCount" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AchievementsList from '@/components/AchievementsList.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const success = ref(null)
const achievementsCount = ref(0)
const achievementsListRef = ref(null)

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

const updateAchievementsCount = (count) => {
  achievementsCount.value = count
}

// Load achievements count on mount
const loadAchievementsCount = async () => {
  try {
    const { gamificationAPI } = await import('@/services/api')
    const response = await gamificationAPI.getMyAchievements()
    achievementsCount.value = response.data.earned_achievements
  } catch (err) {
    console.error('Failed to load achievements count:', err)
  }
}

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch fresh profile data
    await authStore.fetchProfile()

    // Load achievements count
    await loadAchievementsCount()

    // Initialize form with current data
    resetForm()
  } catch (err) {
    error.value = 'Failed to load profile. Please try again.'
    console.error('Profile load error:', err)
  } finally {
    loading.value = false
  }
})
</script>
