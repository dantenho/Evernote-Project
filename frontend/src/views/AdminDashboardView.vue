<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark py-8 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8 flex items-center justify-between animate-fade-in">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-dark-primary mb-2">
            🎛️ Admin Dashboard
          </h1>
          <p class="text-gray-600 dark:text-dark-secondary">
            Analytics, content management, and system configuration
          </p>
        </div>
        <button
          @click="refreshData"
          :disabled="loading"
          class="btn btn-primary flex items-center space-x-2"
        >
          <span :class="{ 'animate-spin': loading }">🔄</span>
          <span>Refresh</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading && !analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="skeleton h-32"></div>
      </div>

      <!-- Analytics Overview Cards -->
      <div v-else class="space-y-8">
        <!-- Key Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Total Users -->
          <div class="card bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 hover:shadow-lg transition-all animate-slide-up">
            <div class="flex items-center justify-between mb-4">
              <span class="text-4xl">👥</span>
              <span class="text-xs px-2 py-1 bg-blue-200 dark:bg-blue-800 text-blue-700 dark:text-blue-200 rounded-full">
                Users
              </span>
            </div>
            <div class="text-3xl font-bold text-blue-900 dark:text-blue-100 mb-1">
              {{ analytics?.total_users || 0 }}
            </div>
            <div class="text-sm text-blue-600 dark:text-blue-300">
              +{{ analytics?.new_users_week || 0 }} this week
            </div>
          </div>

          <!-- Total Tracks -->
          <div class="card bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 hover:shadow-lg transition-all animate-slide-up" style="animation-delay: 0.1s">
            <div class="flex items-center justify-between mb-4">
              <span class="text-4xl">📚</span>
              <span class="text-xs px-2 py-1 bg-purple-200 dark:bg-purple-800 text-purple-700 dark:text-purple-200 rounded-full">
                Tracks
              </span>
            </div>
            <div class="text-3xl font-bold text-purple-900 dark:text-purple-100 mb-1">
              {{ analytics?.total_tracks || 0 }}
            </div>
            <div class="text-sm text-purple-600 dark:text-purple-300">
              {{ analytics?.total_steps || 0 }} total exercises
            </div>
          </div>

          <!-- Completion Rate -->
          <div class="card bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 hover:shadow-lg transition-all animate-slide-up" style="animation-delay: 0.2s">
            <div class="flex items-center justify-between mb-4">
              <span class="text-4xl">✅</span>
              <span class="text-xs px-2 py-1 bg-green-200 dark:bg-green-800 text-green-700 dark:text-green-200 rounded-full">
                Completion
              </span>
            </div>
            <div class="text-3xl font-bold text-green-900 dark:text-green-100 mb-1">
              {{ analytics?.avg_completion_rate || 0 }}%
            </div>
            <div class="text-sm text-green-600 dark:text-green-300">
              Average across all users
            </div>
          </div>

          <!-- AI Generations -->
          <div class="card bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-orange-900/30 dark:to-yellow-900/30 hover:shadow-lg transition-all animate-slide-up" style="animation-delay: 0.3s">
            <div class="flex items-center justify-between mb-4">
              <span class="text-4xl">🤖</span>
              <span class="text-xs px-2 py-1 bg-orange-200 dark:bg-orange-800 text-orange-700 dark:text-orange-200 rounded-full">
                AI Usage
              </span>
            </div>
            <div class="text-3xl font-bold text-orange-900 dark:text-orange-100 mb-1">
              {{ analytics?.ai_generations || 0 }}
            </div>
            <div class="text-sm text-orange-600 dark:text-orange-300">
              Total AI generations
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- User Activity Chart -->
          <div class="card bg-white dark:bg-dark-card">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-dark-primary mb-4 flex items-center">
              <span class="text-2xl mr-2">📊</span>
              User Activity (Last 7 Days)
            </h3>
            <div class="h-64 flex items-end justify-between space-x-2">
              <div
                v-for="(day, index) in analytics?.activity_chart || []"
                :key="index"
                class="flex-1 bg-gradient-to-t from-primary-500 to-primary-400 rounded-t-lg hover:from-primary-600 hover:to-primary-500 transition-all cursor-pointer group relative"
                :style="{ height: `${(day.count / maxActivity) * 100}%` }"
              >
                <div class="absolute -top-8 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  {{ day.count }} users
                </div>
                <div class="text-xs text-center mt-2 text-gray-600 dark:text-dark-secondary">
                  {{ day.label }}
                </div>
              </div>
            </div>
          </div>

          <!-- Top Tracks -->
          <div class="card bg-white dark:bg-dark-card">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-dark-primary mb-4 flex items-center">
              <span class="text-2xl mr-2">🏆</span>
              Most Popular Tracks
            </h3>
            <div class="space-y-3">
              <div
                v-for="(track, index) in analytics?.top_tracks || []"
                :key="track.id"
                class="flex items-center justify-between p-3 bg-gray-50 dark:bg-dark-hover rounded-lg hover:bg-gray-100 dark:hover:bg-dark transition-all"
              >
                <div class="flex items-center space-x-3 flex-1 min-w-0">
                  <span class="text-2xl flex-shrink-0">{{ getRankEmoji(index) }}</span>
                  <div class="min-w-0 flex-1">
                    <div class="font-medium text-gray-900 dark:text-dark-primary truncate">
                      {{ track.title }}
                    </div>
                    <div class="text-sm text-gray-600 dark:text-dark-secondary">
                      {{ track.enrollments }} enrollments
                    </div>
                  </div>
                </div>
                <div class="flex-shrink-0 w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2 ml-4">
                  <div
                    class="bg-gradient-to-r from-primary-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    :style="{ width: `${(track.enrollments / maxEnrollments) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Content Management Section -->
        <div class="card bg-white dark:bg-dark-card">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-dark-primary mb-4 flex items-center">
            <span class="text-2xl mr-2">⚙️</span>
            Quick Actions
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <router-link
              to="/ai-generator"
              class="p-4 border-2 border-dashed border-gray-300 dark:border-dark rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-all text-center group"
            >
              <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🤖</div>
              <div class="font-medium text-gray-900 dark:text-dark-primary">AI Generator</div>
              <div class="text-xs text-gray-600 dark:text-dark-secondary mt-1">
                Create content with AI
              </div>
            </router-link>

            <button
              @click="showMermaidModal = true"
              class="p-4 border-2 border-dashed border-gray-300 dark:border-dark rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-all text-center group"
            >
              <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">📊</div>
              <div class="font-medium text-gray-900 dark:text-dark-primary">Mermaid Diagrams</div>
              <div class="text-xs text-gray-600 dark:text-dark-secondary mt-1">
                Create flowcharts & diagrams
              </div>
            </button>

            <button
              @click="showImageGenModal = true"
              class="p-4 border-2 border-dashed border-gray-300 dark:border-dark rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-all text-center group"
            >
              <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🎨</div>
              <div class="font-medium text-gray-900 dark:text-dark-primary">Image Generator</div>
              <div class="text-xs text-gray-600 dark:text-dark-secondary mt-1">
                Stable Diffusion images
              </div>
            </button>

            <button
              @click="showMCPModal = true"
              class="p-4 border-2 border-dashed border-gray-300 dark:border-dark rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-all text-center group"
            >
              <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🔌</div>
              <div class="font-medium text-gray-900 dark:text-dark-primary">MCP & APIs</div>
              <div class="text-xs text-gray-600 dark:text-dark-secondary mt-1">
                Configure integrations
              </div>
            </button>
          </div>
        </div>

        <!-- Recent Activity Table -->
        <div class="card bg-white dark:bg-dark-card">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-dark-primary mb-4 flex items-center">
            <span class="text-2xl mr-2">📋</span>
            Recent Activity
          </h3>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-dark-hover">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-secondary uppercase tracking-wider">User</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-secondary uppercase tracking-wider">Action</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-secondary uppercase tracking-wider">Content</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-secondary uppercase tracking-wider">Time</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-dark">
                <tr
                  v-for="activity in analytics?.recent_activities || []"
                  :key="activity.id"
                  class="hover:bg-gray-50 dark:hover:bg-dark-hover transition-colors"
                >
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-dark-primary">
                    {{ activity.user }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full"
                      :class="getActionClass(activity.action)">
                      {{ activity.action }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 dark:text-dark-secondary">
                    {{ activity.content }}
                  </td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-dark-muted">
                    {{ activity.time }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Mermaid Modal (placeholder for now) -->
    <div v-if="showMermaidModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in" @click="showMermaidModal = false">
      <div class="bg-white dark:bg-dark-card rounded-xl p-6 max-w-2xl mx-4 animate-scale-in" @click.stop>
        <h3 class="text-xl font-bold text-gray-900 dark:text-dark-primary mb-4">Mermaid Diagram Generator</h3>
        <p class="text-gray-600 dark:text-dark-secondary mb-4">This feature will be implemented next!</p>
        <button @click="showMermaidModal = false" class="btn btn-primary">Close</button>
      </div>
    </div>

    <!-- Image Gen Modal -->
    <div v-if="showImageGenModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in" @click="showImageGenModal = false">
      <div class="bg-white dark:bg-dark-card rounded-xl p-6 max-w-2xl mx-4 animate-scale-in" @click.stop>
        <h3 class="text-xl font-bold text-gray-900 dark:text-dark-primary mb-4">Image Generator (Stable Diffusion)</h3>
        <p class="text-gray-600 dark:text-dark-secondary mb-4">This feature will be implemented next!</p>
        <button @click="showImageGenModal = false" class="btn btn-primary">Close</button>
      </div>
    </div>

    <!-- MCP Modal -->
    <div v-if="showMCPModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in" @click="showMCPModal = false">
      <div class="bg-white dark:bg-dark-card rounded-xl p-6 max-w-2xl mx-4 animate-scale-in" @click.stop>
        <h3 class="text-xl font-bold text-gray-900 dark:text-dark-primary mb-4">MCP & API Configuration</h3>
        <p class="text-gray-600 dark:text-dark-secondary mb-4">This feature will be implemented next!</p>
        <button @click="showMCPModal = false" class="btn btn-primary">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

// State
const loading = ref(true)
const analytics = ref(null)
const showMermaidModal = ref(false)
const showImageGenModal = ref(false)
const showMCPModal = ref(false)

// Computed
const maxActivity = computed(() => {
  if (!analytics.value?.activity_chart) return 100
  return Math.max(...analytics.value.activity_chart.map(d => d.count))
})

const maxEnrollments = computed(() => {
  if (!analytics.value?.top_tracks) return 100
  return Math.max(...analytics.value.top_tracks.map(t => t.enrollments))
})

// Methods
const getRankEmoji = (index) => {
  const emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
  return emojis[index] || '📌'
}

const getActionClass = (action) => {
  const classes = {
    'Completed': 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    'Started': 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
    'Generated': 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300',
  }
  return classes[action] || 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    // Mock data for now - will be replaced with real API call
    await new Promise(resolve => setTimeout(resolve, 800))

    analytics.value = {
      total_users: 1247,
      new_users_week: 23,
      total_tracks: 15,
      total_steps: 342,
      avg_completion_rate: 67,
      ai_generations: 1543,
      activity_chart: [
        { label: 'Mon', count: 45 },
        { label: 'Tue', count: 67 },
        { label: 'Wed', count: 52 },
        { label: 'Thu', count: 81 },
        { label: 'Fri', count: 73 },
        { label: 'Sat', count: 38 },
        { label: 'Sun', count: 29 },
      ],
      top_tracks: [
        { id: 1, title: 'Python Basics', enrollments: 456 },
        { id: 2, title: 'JavaScript Fundamentals', enrollments: 389 },
        { id: 3, title: 'Web Development', enrollments: 312 },
        { id: 4, title: 'Data Structures', enrollments: 267 },
        { id: 5, title: 'Algorithms', enrollments: 198 },
      ],
      recent_activities: [
        { id: 1, user: 'João Silva', action: 'Completed', content: 'Python Basics - Lesson 5', time: '2 min ago' },
        { id: 2, user: 'Maria Santos', action: 'Started', content: 'JavaScript Track', time: '15 min ago' },
        { id: 3, user: 'Admin', action: 'Generated', content: 'Quiz: Variables in Python', time: '1 hour ago' },
        { id: 4, user: 'Pedro Costa', action: 'Completed', content: 'Code Challenge: Hello World', time: '2 hours ago' },
        { id: 5, user: 'Ana Lima', action: 'Started', content: 'Web Development Track', time: '3 hours ago' },
      ],
    }
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadAnalytics()
}

// Lifecycle
onMounted(() => {
  // Check if user is admin (you'll need to add this to your user profile)
  // For now, we'll allow everyone to access
  loadAnalytics()
})
</script>
