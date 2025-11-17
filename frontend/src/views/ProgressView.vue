<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">My Progress</h1>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-600">Loading progress data...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ error }}
      </div>

      <!-- Progress Content -->
      <div v-else class="space-y-8">
        <!-- Overall Statistics -->
        <div v-if="progressSummary" class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="card bg-white text-center">
            <div class="text-4xl font-bold text-gray-900 mb-2">{{ progressSummary.total_steps }}</div>
            <div class="text-sm text-gray-600">Total Steps Attempted</div>
          </div>

          <div class="card bg-green-50 text-center">
            <div class="text-4xl font-bold text-green-700 mb-2">{{ progressSummary.completed_steps }}</div>
            <div class="text-sm text-green-600">Completed</div>
          </div>

          <div class="card bg-blue-50 text-center">
            <div class="text-4xl font-bold text-blue-700 mb-2">{{ progressSummary.in_progress_steps }}</div>
            <div class="text-sm text-blue-600">In Progress</div>
          </div>

          <div class="card bg-primary-50 text-center">
            <div class="text-4xl font-bold text-primary-700 mb-2">{{ progressSummary.completion_percentage }}%</div>
            <div class="text-sm text-primary-600">Completion Rate</div>
          </div>
        </div>

        <!-- Progress by Area -->
        <div v-if="progressSummary && progressSummary.areas && progressSummary.areas.length > 0" class="card bg-white">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Progress by Area</h2>

          <div class="space-y-4">
            <div
              v-for="area in progressSummary.areas"
              :key="area.title"
              class="border-l-4 border-primary-500 pl-4"
            >
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-800">{{ area.title }}</h3>
                <span class="text-sm text-gray-600">
                  {{ area.completed_steps }}/{{ area.total_steps }} completed
                </span>
              </div>

              <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all"
                  :style="{ width: `${getAreaPercentage(area)}%` }"
                ></div>
              </div>

              <div class="flex items-center space-x-4 text-sm text-gray-600">
                <span class="text-green-600">✓ {{ area.completed_steps }} completed</span>
                <span class="text-blue-600">⏳ {{ area.in_progress_steps }} in progress</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Completed Steps -->
          <div class="card bg-white">
            <h2 class="text-xl font-bold text-gray-900 mb-4">✓ Recently Completed</h2>

            <div v-if="completedSteps.length > 0" class="space-y-3">
              <div
                v-for="progress in completedSteps"
                :key="progress.id"
                class="p-3 bg-green-50 border border-green-200 rounded-lg"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ progress.step.title }}</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ progress.step.content_type === 'lesson' ? '📖 Lesson' : '❓ Quiz' }}
                    </p>
                  </div>
                  <div class="text-xs text-gray-500 ml-4">
                    {{ formatDate(progress.completed_at) }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              No completed steps yet. Keep learning!
            </div>
          </div>

          <!-- In Progress Steps -->
          <div class="card bg-white">
            <h2 class="text-xl font-bold text-gray-900 mb-4">⏳ In Progress</h2>

            <div v-if="inProgressSteps.length > 0" class="space-y-3">
              <router-link
                v-for="progress in inProgressSteps"
                :key="progress.id"
                :to="{ name: 'Learn', params: { stepId: progress.step.id } }"
                class="block p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-medium text-gray-900">{{ progress.step.title }}</h4>
                    <p class="text-sm text-gray-600 mt-1">
                      {{ progress.step.content_type === 'lesson' ? '📖 Lesson' : '❓ Quiz' }}
                    </p>
                  </div>
                  <span class="text-blue-600 text-sm ml-4">→</span>
                </div>
              </router-link>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              No steps in progress. Start a new lesson!
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="userProgress.length === 0" class="card bg-white text-center py-12">
          <p class="text-gray-600 mb-4">You haven't started any lessons yet.</p>
          <router-link to="/dashboard" class="btn btn-primary">
            Go to Dashboard
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLearningStore } from '@/stores/learning'

const learningStore = useLearningStore()

const loading = ref(true)
const error = ref(null)

const progressSummary = computed(() => learningStore.progressSummary)
const userProgress = computed(() => learningStore.userProgress)

const completedSteps = computed(() => {
  return userProgress.value
    .filter(p => p.status === 'completed')
    .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at))
    .slice(0, 10) // Show last 10 completed
})

const inProgressSteps = computed(() => {
  return userProgress.value
    .filter(p => p.status === 'in_progress')
    .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
})

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    await Promise.all([
      learningStore.fetchUserProgress(),
      learningStore.fetchProgressSummary(),
    ])
  } catch (err) {
    error.value = 'Failed to load progress data. Please try again.'
    console.error('Progress view load error:', err)
  } finally {
    loading.value = false
  }
})

const getAreaPercentage = (area) => {
  if (area.total_steps === 0) return 0
  return Math.round((area.completed_steps / area.total_steps) * 100)
}

const formatDate = (dateString) => {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return 'Today'
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  } else {
    return date.toLocaleDateString()
  }
}
</script>
