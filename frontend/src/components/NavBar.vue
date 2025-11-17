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
