<template>
  <div class="card bg-white">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900">🏆 Achievements</h2>
      <div class="text-sm text-gray-600">
        {{ achievementsData.earned_achievements }} / {{ achievementsData.total_achievements }} earned
        <span class="ml-2 text-primary-600 font-semibold">
          ({{ achievementsData.completion_percentage }}%)
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="text-gray-600">Loading achievements...</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>

    <!-- Achievements Grid -->
    <div v-else>
      <!-- Recent Earned Achievements -->
      <div v-if="achievementsData.recent_achievements && achievementsData.recent_achievements.length > 0">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Recently Earned</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div
            v-for="userAchievement in achievementsData.recent_achievements"
            :key="userAchievement.id"
            class="flex items-start space-x-3 p-4 border-2 border-primary-300 rounded-lg bg-gradient-to-r from-primary-50 to-purple-50 hover:shadow-md transition-shadow"
          >
            <!-- Achievement Icon -->
            <div class="text-3xl flex-shrink-0">
              {{ userAchievement.achievement.icon }}
            </div>

            <!-- Achievement Details -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between">
                <h4 class="font-bold text-gray-900 text-sm">
                  {{ userAchievement.achievement.name }}
                </h4>
                <span class="ml-2 text-xs font-semibold text-primary-600 whitespace-nowrap">
                  +{{ userAchievement.xp_awarded }} XP
                </span>
              </div>
              <p class="text-xs text-gray-600 mt-1">
                {{ userAchievement.achievement.description }}
              </p>
              <div class="flex items-center mt-2 text-xs text-gray-500">
                <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                {{ formatDate(userAchievement.earned_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
        <div class="text-4xl mb-3">🎯</div>
        <h3 class="text-lg font-semibold text-gray-700 mb-2">No achievements yet!</h3>
        <p class="text-gray-600">
          Complete your first step to start earning achievements
        </p>
      </div>

      <!-- All Available Achievements -->
      <div v-if="allAchievements.length > 0" class="mt-8">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">All Achievements</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="achievement in allAchievements"
            :key="achievement.id"
            class="flex items-start space-x-3 p-3 border rounded-lg transition-all"
            :class="isEarned(achievement.id)
              ? 'border-primary-200 bg-primary-50'
              : 'border-gray-200 bg-gray-50 opacity-60'"
          >
            <!-- Achievement Icon -->
            <div class="text-2xl flex-shrink-0">
              {{ achievement.icon }}
            </div>

            <!-- Achievement Details -->
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 text-sm">
                {{ achievement.name }}
              </h4>
              <p class="text-xs text-gray-600 mt-1 line-clamp-2">
                {{ achievement.description }}
              </p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs font-medium text-primary-600">
                  +{{ achievement.xp_reward }} XP
                </span>
                <span
                  v-if="isEarned(achievement.id)"
                  class="text-xs font-semibold text-green-600"
                >
                  ✓ Earned
                </span>
                <span
                  v-else
                  class="text-xs text-gray-500"
                >
                  🔒 Locked
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { gamificationAPI } from '@/services/api'

// State
const loading = ref(true)
const error = ref(null)
const achievementsData = ref({
  total_achievements: 0,
  earned_achievements: 0,
  completion_percentage: 0,
  recent_achievements: []
})
const allAchievements = ref([])

// Computed
const earnedAchievementIds = computed(() => {
  return new Set(
    achievementsData.value.recent_achievements.map(ua => ua.achievement.id)
  )
})

// Methods
const isEarned = (achievementId) => {
  return earnedAchievementIds.value.has(achievementId)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const loadAchievements = async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch user's achievements
    const userResponse = await gamificationAPI.getMyAchievements()
    achievementsData.value = userResponse.data

    // Fetch all available achievements
    const allResponse = await gamificationAPI.getAvailableAchievements()
    allAchievements.value = allResponse.data

  } catch (err) {
    error.value = 'Failed to load achievements. Please try again.'
    console.error('Error loading achievements:', err)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAchievements()
})

// Expose refresh method for parent components
defineExpose({
  refresh: loadAchievements
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
