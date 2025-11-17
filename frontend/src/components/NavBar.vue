<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/dashboard" class="text-2xl font-bold text-primary-600">
              🎓 LearnHub
            </router-link>
          </div>
          <div class="hidden sm:ml-8 sm:flex sm:space-x-8">
            <router-link
              to="/dashboard"
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="isActive('/dashboard')"
            >
              Dashboard
            </router-link>
            <router-link
              to="/progress"
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              :class="isActive('/progress')"
            >
              My Progress
            </router-link>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700">
            👋 {{ authStore.user?.first_name || 'User' }}
          </div>

          <!-- XP and Level Display -->
          <div v-if="authStore.user?.profile" class="flex items-center space-x-3 px-3 py-1 bg-gradient-to-r from-primary-50 to-purple-50 rounded-lg border border-primary-200">
            <!-- Level Badge -->
            <div class="flex items-center space-x-1">
              <span class="text-xs font-semibold text-primary-700">⭐ Level</span>
              <span class="text-sm font-bold text-primary-900">{{ authStore.user.profile.level }}</span>
            </div>

            <!-- Vertical Divider -->
            <div class="h-6 w-px bg-primary-300"></div>

            <!-- XP Progress -->
            <div class="flex flex-col">
              <div class="flex items-center space-x-2">
                <span class="text-xs text-gray-600">
                  {{ authStore.user.profile.xp_for_current_level }} / {{ authStore.user.profile.xp_for_next_level }} XP
                </span>
              </div>
              <!-- Progress Bar -->
              <div class="w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden mt-0.5">
                <div
                  class="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all duration-300"
                  :style="{ width: `${authStore.user.profile.progress_to_next_level}%` }"
                ></div>
              </div>
            </div>
          </div>

          <router-link
            to="/profile"
            class="text-gray-600 hover:text-gray-900"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
          <button
            @click="handleLogout"
            class="text-gray-600 hover:text-gray-900"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isActive = (path) => {
  return route.path === path
    ? 'border-primary-500 text-gray-900'
    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
