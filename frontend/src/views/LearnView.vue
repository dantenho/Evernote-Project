<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-600">Loading...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ error }}
        <div class="mt-4">
          <router-link to="/dashboard" class="btn btn-secondary">
            Back to Dashboard
          </router-link>
        </div>
      </div>

      <!-- Step Content -->
      <div v-else-if="step" class="space-y-6">
        <!-- Header -->
        <div class="card bg-white">
          <div class="flex items-center justify-between mb-4">
            <router-link
              to="/dashboard"
              class="text-primary-600 hover:text-primary-700 flex items-center space-x-2"
            >
              <span>←</span>
              <span>Back to Dashboard</span>
            </router-link>

            <span
              v-if="isCompleted"
              class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
            >
              ✓ Completed
            </span>
          </div>

          <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ step.title }}</h1>
          <div class="flex items-center space-x-4 text-sm text-gray-600">
            <span class="px-2 py-1 bg-gray-100 rounded">
              {{ step.content_type === 'lesson' ? '📖 Lesson' : '❓ Quiz' }}
            </span>
            <span v-if="step.estimated_time">⏱️ {{ step.estimated_time }} min</span>
          </div>
        </div>

        <!-- Lesson Content -->
        <div v-if="step.content_type === 'lesson'" class="space-y-6">
          <div v-if="step.video_url" class="card bg-white">
            <div class="aspect-w-16 aspect-h-9 bg-gray-200 rounded-lg overflow-hidden">
              <iframe
                :src="step.video_url"
                class="w-full h-full"
                style="min-height: 400px"
                frameborder="0"
                allowfullscreen
              ></iframe>
            </div>
          </div>

          <div v-if="step.text_content" class="card bg-white prose max-w-none">
            <div v-html="step.text_content"></div>
          </div>

          <div class="card bg-white">
            <button
              @click="completeStep"
              :disabled="completingStep || isCompleted"
              class="w-full btn btn-primary"
              :class="{ 'opacity-50 cursor-not-allowed': isCompleted }"
            >
              {{ isCompleted ? 'Already Completed' : completingStep ? 'Marking Complete...' : 'Mark as Complete' }}
            </button>
          </div>
        </div>

        <!-- Quiz Content -->
        <div v-else-if="step.content_type === 'quiz'" class="space-y-6">
          <div
            v-for="(question, qIndex) in step.questions"
            :key="question.id"
            class="card bg-white"
          >
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Question {{ qIndex + 1 }}: {{ question.text }}
            </h3>

            <div class="space-y-2">
              <label
                v-for="choice in question.choices"
                :key="choice.id"
                class="flex items-start space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-colors"
                :class="getChoiceClass(question.id, choice.id)"
              >
                <input
                  type="radio"
                  :name="`question-${question.id}`"
                  :value="choice.id"
                  v-model="answers[question.id]"
                  :disabled="submitted"
                  class="mt-1"
                />
                <span class="flex-1">{{ choice.text }}</span>
                <span v-if="submitted && choice.is_correct" class="text-green-600 font-bold">
                  ✓
                </span>
              </label>
            </div>

            <div v-if="submitted && question.explanation" class="mt-4 p-4 bg-blue-50 rounded-lg">
              <p class="text-sm text-blue-900">
                <strong>Explanation:</strong> {{ question.explanation }}
              </p>
            </div>
          </div>

          <div class="card bg-white">
            <button
              v-if="!submitted"
              @click="submitQuiz"
              :disabled="!allQuestionsAnswered || completingStep"
              class="w-full btn btn-primary"
              :class="{ 'opacity-50 cursor-not-allowed': !allQuestionsAnswered }"
            >
              {{ completingStep ? 'Submitting...' : 'Submit Quiz' }}
            </button>

            <div v-else>
              <div class="mb-4 p-4 rounded-lg" :class="quizPassed ? 'bg-green-50' : 'bg-red-50'">
                <p class="text-lg font-semibold" :class="quizPassed ? 'text-green-800' : 'text-red-800'">
                  {{ quizPassed ? '🎉 Great job! You passed!' : '❌ Not quite. Review and try again.' }}
                </p>
                <p class="text-sm mt-2" :class="quizPassed ? 'text-green-700' : 'text-red-700'">
                  Score: {{ quizScore.correct }}/{{ quizScore.total }} ({{ quizScorePercentage }}%)
                </p>
              </div>

              <button
                v-if="!quizPassed"
                @click="resetQuiz"
                class="w-full btn btn-secondary"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLearningStore } from '@/stores/learning'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const learningStore = useLearningStore()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(null)
const completingStep = ref(false)
const answers = ref({})
const submitted = ref(false)

const stepId = computed(() => route.params.stepId)
const step = computed(() => learningStore.getStepById(stepId.value))
const isCompleted = computed(() => learningStore.isStepCompleted(stepId.value))

const allQuestionsAnswered = computed(() => {
  if (!step.value || step.value.content_type !== 'quiz') return false
  return step.value.questions.every(q => answers.value[q.id] !== undefined)
})

const quizScore = computed(() => {
  if (!step.value || step.value.content_type !== 'quiz' || !submitted.value) {
    return { correct: 0, total: 0 }
  }

  let correct = 0
  const total = step.value.questions.length

  step.value.questions.forEach(question => {
    const selectedChoiceId = answers.value[question.id]
    const selectedChoice = question.choices.find(c => c.id === selectedChoiceId)
    if (selectedChoice && selectedChoice.is_correct) {
      correct++
    }
  })

  return { correct, total }
})

const quizScorePercentage = computed(() => {
  if (quizScore.value.total === 0) return 0
  return Math.round((quizScore.value.correct / quizScore.value.total) * 100)
})

const quizPassed = computed(() => {
  return quizScorePercentage.value >= 70
})

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch learning paths if not already loaded
    if (learningStore.allAreas.length === 0) {
      await learningStore.fetchLearningPaths()
    }

    // Fetch user progress
    await learningStore.fetchUserProgress()

    // Verify step exists
    if (!step.value) {
      error.value = 'Step not found'
    }
  } catch (err) {
    error.value = 'Failed to load step content. Please try again.'
    console.error('Learn view load error:', err)
  } finally {
    loading.value = false
  }
})

const getChoiceClass = (questionId, choiceId) => {
  const isSelected = answers.value[questionId] === choiceId

  if (!submitted.value) {
    return isSelected ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-300'
  }

  // After submission, show correct/incorrect
  const question = step.value.questions.find(q => q.id === questionId)
  const choice = question.choices.find(c => c.id === choiceId)

  if (choice.is_correct) {
    return 'border-green-500 bg-green-50'
  } else if (isSelected) {
    return 'border-red-500 bg-red-50'
  }

  return 'border-gray-300 bg-gray-50'
}

const submitQuiz = async () => {
  submitted.value = true

  // If passed, mark as complete
  if (quizPassed.value) {
    await completeStep()
  }
}

const resetQuiz = () => {
  answers.value = {}
  submitted.value = false
}

const completeStep = async () => {
  if (isCompleted.value) return

  completingStep.value = true

  const result = await learningStore.completeStep(stepId.value)

  if (result.success) {
    // Refresh user profile to update XP and level in navbar
    await authStore.fetchProfile()

    // Log XP earned if available
    if (result.data?.xp_earned) {
      console.log(`🎉 Step complete! +${result.data.xp_earned} XP earned!`)

      if (result.data.leveled_up) {
        console.log(`🌟 LEVEL UP! You reached level ${result.data.level}!`)
      }
    }
  } else {
    error.value = 'Failed to mark step as complete. Please try again.'
  }

  completingStep.value = false
}
</script>
