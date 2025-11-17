<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header with Progress Summary -->
      <div class="mb-8 animate-fade-in">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">🎓 My Learning Dashboard</h1>

        <div v-if="progressSummary" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div class="card bg-white hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.1s">
            <div class="text-sm text-gray-600 mb-1">Total Steps</div>
            <div class="text-2xl font-bold text-gray-900">{{ progressSummary.total_steps }}</div>
          </div>
          <div class="card bg-gradient-to-br from-green-50 to-emerald-50 hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.2s">
            <div class="text-sm text-green-600 mb-1">✅ Completed</div>
            <div class="text-2xl font-bold text-green-700">{{ progressSummary.completed_steps }}</div>
          </div>
          <div class="card bg-gradient-to-br from-blue-50 to-cyan-50 hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.3s">
            <div class="text-sm text-blue-600 mb-1">🚀 In Progress</div>
            <div class="text-2xl font-bold text-blue-700">{{ progressSummary.in_progress_steps }}</div>
          </div>
          <div class="card bg-gradient-to-br from-primary-50 to-purple-50 hover:shadow-md transition-shadow animate-slide-up" style="animation-delay: 0.4s">
            <div class="text-sm text-primary-600 mb-1">📊 Completion</div>
            <div class="text-2xl font-bold text-primary-700">{{ progressSummary.completion_percentage }}%</div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-600">Loading learning paths...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ error }}
      </div>

      <!-- Learning Areas -->
      <div v-else class="space-y-6">
        <div v-for="area in learningPaths" :key="area.id" class="card bg-white">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">{{ area.title }}</h2>
          <p v-if="area.description" class="text-gray-600 mb-6">{{ area.description }}</p>

          <!-- Topics -->
          <div class="space-y-4">
            <div v-for="topic in area.topics" :key="topic.id" class="border-l-4 border-primary-500 pl-4">
              <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ topic.title }}</h3>
              <p v-if="topic.description" class="text-gray-600 mb-4 text-sm">{{ topic.description }}</p>

              <!-- Tracks -->
              <div class="space-y-3">
                <div
                  v-for="track in topic.tracks"
                  :key="track.id"
                  class="bg-gradient-to-br from-white to-gray-50 rounded-lg p-5 border border-gray-200 hover:border-primary-300 transition-all shadow-sm hover:shadow-md"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <h4 class="text-lg font-semibold text-gray-900 mb-1">{{ track.icon || '📚' }} {{ track.title }}</h4>
                      <p v-if="track.description" class="text-gray-600 text-sm mb-3">{{ track.description }}</p>
                      <div class="flex items-center space-x-3 text-sm text-gray-600">
                        <span>{{ track.steps?.length || 0 }} exercises</span>
                        <span v-if="track.difficulty" class="px-2 py-0.5 rounded-full bg-gray-200 text-xs font-medium">
                          {{ track.difficulty }}
                        </span>
                      </div>
                    </div>
                    <span
                      class="px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ml-3"
                      :class="getTrackProgressClass(track)"
                    >
                      {{ getTrackProgress(track) }}
                    </span>
                  </div>

                  <!-- Progress Bar -->
                  <div v-if="track.steps && track.steps.length > 0" class="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-4">
                    <div
                      class="h-full bg-gradient-to-r from-primary-500 to-purple-500 transition-all duration-500"
                      :style="{ width: `${getTrackProgressPercentage(track)}%` }"
                    ></div>
                  </div>

                  <!-- Start/Continue Button -->
                  <button
                    v-if="track.steps && track.steps.length > 0"
                    @click="startTrack(track)"
                    class="btn btn-primary w-full mb-4 flex items-center justify-center space-x-2 py-3 shadow-md hover:shadow-lg transform hover:scale-105 transition-all"
                  >
                    <span>{{ getTrackProgressPercentage(track) === 0 ? '🚀 Start Track' : '▶️ Continue Learning' }}</span>
                  </button>

                  <!-- Steps (collapsible) -->
                  <details class="group">
                    <summary class="cursor-pointer text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center space-x-1">
                      <span class="transform transition-transform group-open:rotate-90">▶</span>
                      <span>View {{ track.steps?.length || 0 }} Exercises</span>
                    </summary>
                    <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                      <button
                        v-for="step in track.steps"
                        :key="step.id"
                        @click="navigateToStep(track, step)"
                        class="flex items-center justify-between p-3 rounded-md border transition-all hover:shadow-md text-left"
                        :class="getStepClass(step)"
                      >
                        <div class="flex items-center space-x-2 min-w-0">
                          <span class="text-xl flex-shrink-0">{{ getStepIcon(step) }}</span>
                          <span class="text-sm font-medium truncate">{{ step.title }}</span>
                        </div>
                        <span v-if="isStepCompleted(step.id)" class="text-green-600 flex-shrink-0 text-lg">
                          ✓
                        </span>
                      </button>
                    </div>
                  </details>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="learningPaths.length === 0" class="text-center py-12">
          <p class="text-gray-600">No learning paths available yet. Check back soon!</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learning'

const router = useRouter()
const learningStore = useLearningStore()

const loading = ref(false)
const error = ref(null)

const learningPaths = computed(() => learningStore.allAreas)
const progressSummary = computed(() => learningStore.progressSummary)

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch learning paths and user progress in parallel
    await Promise.all([
      learningStore.fetchLearningPaths(),
      learningStore.fetchUserProgress(),
      learningStore.fetchProgressSummary(),
    ])
  } catch (err) {
    error.value = 'Failed to load learning content. Please try again.'
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
})

const isStepCompleted = (stepId) => {
  return learningStore.isStepCompleted(stepId)
}

const getStepIcon = (step) => {
  if (step.content_type === 'lesson') {
    return '📖'
  } else if (step.content_type === 'quiz') {
    return '❓'
  }
  return '📝'
}

const getStepClass = (step) => {
  if (isStepCompleted(step.id)) {
    return 'border-green-300 bg-green-50 hover:bg-green-100'
  }
  return 'border-gray-300 bg-white hover:bg-gray-50'
}

const getTrackProgress = (track) => {
  if (!track.steps || track.steps.length === 0) {
    return '0/0'
  }

  const completed = track.steps.filter(step => isStepCompleted(step.id)).length
  return `${completed}/${track.steps.length}`
}

const getTrackProgressClass = (track) => {
  if (!track.steps || track.steps.length === 0) {
    return 'bg-gray-200 text-gray-700'
  }

  const completed = track.steps.filter(step => isStepCompleted(step.id)).length
  const percentage = (completed / track.steps.length) * 100

  if (percentage === 100) {
    return 'bg-green-200 text-green-800'
  } else if (percentage > 0) {
    return 'bg-blue-200 text-blue-800'
  }
  return 'bg-gray-200 text-gray-700'
}

const getTrackProgressPercentage = (track) => {
  if (!track.steps || track.steps.length === 0) {
    return 0
  }

  const completed = track.steps.filter(step => isStepCompleted(step.id)).length
  return Math.round((completed / track.steps.length) * 100)
}

const startTrack = (track) => {
  // Find first incomplete step, or start from beginning
  const firstIncompleteStep = track.steps.find(step => !isStepCompleted(step.id))
  const stepToStart = firstIncompleteStep || track.steps[0]

  if (stepToStart) {
    router.push({
      name: 'StepExercise',
      params: {
        trackId: track.id,
        stepId: stepToStart.id
      }
    })
  }
}

const navigateToStep = (track, step) => {
  router.push({
    name: 'StepExercise',
    params: {
      trackId: track.id,
      stepId: step.id
    }
  })
}
</script>
