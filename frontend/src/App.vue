<template>
  <div id="app" class="min-h-screen flex flex-col">
    <NavBar v-if="authStore.isAuthenticated" />
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // Initialize auth state from localStorage
  await authStore.initAuth()
})
</script>
