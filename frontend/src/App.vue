<template>
  <div id="app" class="min-h-screen flex flex-col bg-white dark:bg-dark text-gray-900 dark:text-dark-primary transition-colors duration-300">
    <NavBar v-if="authStore.isAuthenticated" />
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import NavBar from '@/components/NavBar.vue'

const authStore = useAuthStore()
const { initTheme } = useTheme()

onMounted(async () => {
  // Initialize theme from localStorage or system preference
  initTheme()

  // Initialize auth state from localStorage
  await authStore.initAuth()
})
</script>
