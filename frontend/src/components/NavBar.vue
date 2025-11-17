<template>
  <nav class="bg-white dark:bg-dark-card shadow-sm border-b border-gray-200 dark:border-dark transition-colors duration-300">
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
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
              :class="isActive('/dashboard')"
            >
              Dashboard
            </router-link>
            <router-link
              to="/progress"
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
              :class="isActive('/progress')"
            >
              My Progress
            </router-link>
            <router-link
              to="/ai-generator"
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
              :class="isActive('/ai-generator')"
            >
              🤖 AI Generator
            </router-link>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-700 dark:text-dark-secondary">
            👋 {{ authStore.user?.first_name || 'User' }}
          </div>

          <!-- Rank and XP Display - Desktop -->
          <div v-if="authStore.user?.profile" class="hidden md:flex items-center space-x-3 px-3 py-1.5 bg-gradient-to-r from-primary-50 via-purple-50 to-pink-50 rounded-lg border border-primary-200 shadow-sm hover:shadow-md transition-all duration-300">
            <!-- Rank Badge -->
            <div class="flex items-center space-x-1.5">
              <span class="text-lg">{{ authStore.user.profile.rank_icon || '🏆' }}</span>
              <div class="flex flex-col">
                <span class="text-xs font-semibold" :style="{ color: authStore.user.profile.rank_color || '#000' }">
                  {{ authStore.user.profile.rank_name || 'Latão' }}
                </span>
                <span class="text-xs text-gray-500">{{ authStore.user.profile.xp_points }} XP</span>
              </div>
            </div>

            <!-- Vertical Divider -->
            <div class="h-8 w-px bg-primary-300"></div>

            <!-- XP Progress to Next Rank -->
            <div class="flex flex-col min-w-[100px]">
              <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>{{ authStore.user.profile.xp_in_current_rank || 0 }}</span>
                <span class="text-gray-400">/</span>
                <span>{{ authStore.user.profile.xp_for_next_rank || 100 }} XP</span>
              </div>
              <!-- Progress Bar -->
              <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500 ease-out"
                  :style="{
                    width: `${authStore.user.profile.progress_to_next_rank || 0}%`,
                    background: `linear-gradient(90deg, ${authStore.user.profile.rank_color || '#3B82F6'}, ${authStore.user.profile.rank_color || '#8B5CF6'})`
                  }"
                ></div>
              </div>
              <span v-if="authStore.user.profile.next_rank_name" class="text-xs text-gray-500 mt-0.5">
                Próximo: {{ authStore.user.profile.next_rank_name }}
              </span>
            </div>

            <!-- Streak Display (if exists) -->
            <div v-if="authStore.user.profile.current_streak > 0" class="flex items-center space-x-1 pl-2 border-l border-primary-200">
              <span class="text-lg">🔥</span>
              <span class="text-sm font-bold text-orange-600">{{ authStore.user.profile.current_streak }}</span>
            </div>
          </div>

          <!-- Mobile Compact View -->
          <div v-if="authStore.user?.profile" class="md:hidden flex items-center space-x-2">
            <span class="text-base">{{ authStore.user.profile.rank_icon || '🏆' }}</span>
            <span class="text-sm font-semibold" :style="{ color: authStore.user.profile.rank_color || '#000' }">
              {{ authStore.user.profile.rank_name || 'Latão' }}
            </span>
            <span v-if="authStore.user.profile.current_streak > 0" class="flex items-center space-x-0.5">
              <span class="text-sm">🔥</span>
              <span class="text-xs font-bold text-orange-600">{{ authStore.user.profile.current_streak }}</span>
            </span>
          </div>

          <!-- Theme Toggle Button -->
          <button
            @click="toggleTheme"
            class="text-gray-600 hover:text-gray-900 dark:text-dark-secondary dark:hover:text-dark-primary transition-colors p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-hover"
            title="Toggle dark mode"
          >
            <!-- Sun icon (shown in dark mode) -->
            <svg v-if="isDark" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <!-- Moon icon (shown in light mode) -->
            <svg v-else class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>

          <router-link
            to="/profile"
            class="text-gray-600 hover:text-gray-900 dark:text-dark-secondary dark:hover:text-dark-primary transition-colors"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </router-link>
          <button
            @click="handleLogout"
            class="text-gray-600 hover:text-gray-900 dark:text-dark-secondary dark:hover:text-dark-primary transition-colors"
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
import { useTheme } from '@/composables/useTheme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { isDark, toggleTheme } = useTheme()

const isActive = (path) => {
  return route.path === path
    ? 'border-primary-500 text-gray-900 dark:text-dark-primary'
    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-dark-secondary dark:hover:text-dark-primary'
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
