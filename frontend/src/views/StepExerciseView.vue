<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-purple-50 to-pink-50">
    <!-- Progress Bar at Top -->
    <div class="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-3">
        <div class="flex items-center justify-between mb-2">
          <button
            @click="handleBack"
            class="text-gray-600 hover:text-gray-900 transition-colors"
          >
            ← Back
          </button>
          <div class="flex items-center space-x-2 text-sm">
            <span class="font-semibold text-primary-600">{{ currentStepNumber }}/{{ totalSteps }}</span>
            <span class="text-gray-500">{{ currentStep?.title }}</span>
          </div>
          <div class="flex items-center space-x-1 text-yellow-600">
            <span class="text-xl">⚡</span>
            <span class="font-bold">{{ currentStep?.xp_reward || 10 }} XP</span>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-primary-500 to-purple-500 transition-all duration-500 ease-out"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="pt-24 pb-12 px-4">
      <div class="max-w-3xl mx-auto">
        <div v-if="loading" class="text-center py-20">
          <div class="inline-block animate-spin text-6xl mb-4">⚙️</div>
          <p class="text-gray-600">Loading exercise...</p>
        </div>

        <div v-else-if="error" class="card bg-red-50 border-red-200 animate-scale-in">
          <p class="text-red-800">❌ {{ error }}</p>
          <button @click="loadStep" class="btn btn-primary mt-4">Try Again</button>
        </div>

        <!-- Lesson Content -->
        <div v-else-if="currentStep && currentStep.content_type === 'lesson'" class="space-y-6 animate-fade-in">
          <!-- Lesson Card -->
          <div class="card bg-white shadow-xl">
            <h1 class="text-3xl font-bold text-gray-900 mb-4">
              {{ currentStep.title }}
            </h1>

            <!-- Lesson Content -->
            <div
              class="prose prose-lg max-w-none mb-6"
              v-html="currentStep.text_content"
            ></div>

            <!-- Code Snippet -->
            <div v-if="currentStep.code_snippet" class="mt-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold text-gray-900">💻 Try It Yourself</h3>
                <button
                  @click="copyCode"
                  class="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  📋 Copy Code
                </button>
              </div>
              <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto"><code>{{ currentStep.code_snippet }}</code></pre>
            </div>

            <!-- Video Embed -->
            <div v-if="currentStep.video_url" class="mt-6">
              <div class="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden">
                <iframe
                  :src="currentStep.video_url"
                  frameborder="0"
                  allowfullscreen
                  class="w-full h-full"
                ></iframe>
              </div>
            </div>
          </div>

          <!-- Continue Button -->
          <div class="flex justify-end">
            <button
              @click="completeAndNext"
              :disabled="completing"
              class="btn btn-primary btn-lg flex items-center space-x-2 px-8 py-4 text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
            >
              <span>{{ completing ? 'Completing...' : 'Continue' }}</span>
              <span>→</span>
            </button>
          </div>
        </div>

        <!-- Code Challenge Content -->
        <div v-else-if="currentStep && currentStep.content_type === 'code_challenge'" class="space-y-6 animate-fade-in">
          <!-- Challenge Card -->
          <div class="card bg-white shadow-xl">
            <div class="flex items-center justify-between mb-4">
              <h1 class="text-2xl font-bold text-gray-900">
                💻 {{ currentStep.title }}
              </h1>
              <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold">
                Code Challenge
              </span>
            </div>

            <!-- Challenge Instructions -->
            <div
              v-if="currentStep.text_content"
              class="prose prose-lg max-w-none mb-6"
              v-html="currentStep.text_content"
            ></div>

            <!-- Code Editor Component -->
            <CodeEditor
              :initial-code="currentStep.code_snippet || '# Write your code here\\nprint(\"Hello\")'"
              :expected-output="currentStep.expected_output"
              :solution="currentStep.solution"
              :show-solution="codeAttempts >= 3"
              :hints="getCodeHints()"
              @correct="handleCodeCorrect"
              @run="handleCodeRun"
              @error="handleCodeError"
            />
          </div>

          <!-- Navigation Button -->
          <div class="flex justify-end">
            <button
              v-if="codeIsCorrect"
              @click="completeAndNext"
              :disabled="completing"
              class="btn btn-primary btn-lg flex items-center space-x-2 px-8 py-4 text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all animate-bounce-subtle"
            >
              <span>{{ completing ? 'Completing...' : 'Continue' }}</span>
              <span>→</span>
            </button>
            <button
              v-else
              disabled
              class="btn btn-secondary btn-lg flex items-center space-x-2 px-8 py-4 text-lg opacity-50 cursor-not-allowed"
            >
              <span>Complete the challenge to continue</span>
            </button>
          </div>
        </div>

        <!-- Quiz Content -->
        <div v-else-if="currentStep && currentStep.content_type === 'quiz'" class="space-y-6 animate-fade-in">
          <!-- Quiz Question Card -->
          <div v-if="currentQuestion" class="card bg-white shadow-xl">
            <div class="mb-4">
              <span class="text-sm font-semibold text-primary-600">
                Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }}
              </span>
            </div>

            <h2 class="text-2xl font-bold text-gray-900 mb-6">
              {{ currentQuestion.text }}
            </h2>

            <!-- Answer Options -->
            <div class="space-y-3">
              <button
                v-for="(alternative, index) in currentQuestion.alternatives"
                :key="alternative.id"
                @click="selectAnswer(alternative)"
                :disabled="answerSelected"
                :class="[
                  'w-full p-4 rounded-lg border-2 text-left transition-all font-medium',
                  getAlternativeClass(alternative),
                  answerSelected ? 'cursor-not-allowed' : 'cursor-pointer hover:border-primary-300 hover:bg-primary-50'
                ]"
              >
                <div class="flex items-center">
                  <span class="flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center mr-3"
                    :class="getCircleClass(alternative)">
                    {{ String.fromCharCode(65 + index) }}
                  </span>
                  <span class="flex-1">{{ alternative.text }}</span>
                  <span v-if="answerSelected && alternative.is_correct" class="text-2xl">✓</span>
                  <span v-if="answerSelected && selectedAlternative?.id === alternative.id && !alternative.is_correct" class="text-2xl">✗</span>
                </div>
              </button>
            </div>

            <!-- Explanation -->
            <div v-if="answerSelected && selectedAlternative" class="mt-6 p-4 rounded-lg animate-scale-in"
              :class="selectedAlternative.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
              <div class="flex items-start space-x-3">
                <span class="text-3xl flex-shrink-0">
                  {{ selectedAlternative.is_correct ? '🎉' : '💡' }}
                </span>
                <div>
                  <h4 class="font-bold mb-1" :class="selectedAlternative.is_correct ? 'text-green-800' : 'text-red-800'">
                    {{ selectedAlternative.is_correct ? 'Correct!' : 'Not quite!' }}
                  </h4>
                  <p class="text-sm" :class="selectedAlternative.is_correct ? 'text-green-700' : 'text-red-700'">
                    {{ selectedAlternative.explanation || (selectedAlternative.is_correct ? 'Great job!' : 'Try again!') }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex justify-between items-center">
            <button
              v-if="currentQuestionIndex > 0"
              @click="previousQuestion"
              class="btn btn-secondary flex items-center space-x-2"
            >
              <span>←</span>
              <span>Previous</span>
            </button>
            <div v-else></div>

            <button
              v-if="answerSelected"
              @click="nextQuestionOrComplete"
              :disabled="completing"
              class="btn btn-primary flex items-center space-x-2 px-6 py-3 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
            >
              <span>{{ completing ? 'Completing...' : (isLastQuestion ? 'Complete Quiz' : 'Next Question') }}</span>
              <span>→</span>
            </button>
          </div>

          <!-- Quiz Progress Dots -->
          <div class="flex justify-center space-x-2 mt-4">
            <div
              v-for="(q, index) in currentStep.questions"
              :key="index"
              class="w-3 h-3 rounded-full transition-all"
              :class="index === currentQuestionIndex ? 'bg-primary-600 scale-125' : (index < currentQuestionIndex ? 'bg-green-500' : 'bg-gray-300')"
            ></div>
          </div>
        </div>

        <!-- Completion Celebration -->
        <div v-if="showCelebration" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in">
          <div class="bg-white rounded-2xl p-8 max-w-md mx-4 text-center animate-scale-in shadow-2xl">
            <div class="text-6xl mb-4 animate-bounce">🎉</div>
            <h2 class="text-3xl font-bold text-gray-900 mb-2">Awesome!</h2>
            <p class="text-lg text-gray-600 mb-4">You've earned {{ currentStep?.xp_reward || 10 }} XP</p>

            <div class="flex items-center justify-center space-x-4 mb-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg">
              <span class="text-4xl">⚡</span>
              <div class="text-left">
                <div class="text-2xl font-bold text-orange-600">+{{ currentStep?.xp_reward || 10 }} XP</div>
                <div class="text-sm text-gray-600">Total: {{ authStore.user?.profile?.xp_points || 0 }} XP</div>
              </div>
            </div>

            <button
              @click="continueToNext"
              class="btn btn-primary w-full text-lg py-3"
            >
              {{ hasNextStep ? 'Continue →' : 'Back to Track 🎯' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { learningAPI, progressAPI } from '@/services/api'
import CodeEditor from '@/components/CodeEditor.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// ============================================================================
// State
// ============================================================================

const loading = ref(true)
const error = ref('')
const currentStep = ref(null)
const allSteps = ref([])
const completing = ref(false)
const showCelebration = ref(false)

// Quiz state
const currentQuestionIndex = ref(0)
const answerSelected = ref(false)
const selectedAlternative = ref(null)
const quizAnswers = ref([])

// Code challenge state
const codeIsCorrect = ref(false)
const codeAttempts = ref(0)
const codeOutput = ref('')

// ============================================================================
// Computed
// ============================================================================

const stepId = computed(() => parseInt(route.params.stepId))
const currentStepNumber = computed(() => {
  const index = allSteps.value.findIndex(s => s.id === stepId.value)
  return index >= 0 ? index + 1 : 1
})
const totalSteps = computed(() => allSteps.value.length)
const progressPercentage = computed(() => {
  if (totalSteps.value === 0) return 0
  return (currentStepNumber.value / totalSteps.value) * 100
})

const currentQuestion = computed(() => {
  if (!currentStep.value || !currentStep.value.questions) return null
  return currentStep.value.questions[currentQuestionIndex.value]
})

const totalQuestions = computed(() => {
  return currentStep.value?.questions?.length || 0
})

const isLastQuestion = computed(() => {
  return currentQuestionIndex.value === totalQuestions.value - 1
})

const hasNextStep = computed(() => {
  const currentIndex = allSteps.value.findIndex(s => s.id === stepId.value)
  return currentIndex >= 0 && currentIndex < allSteps.value.length - 1
})

// ============================================================================
// Methods
// ============================================================================

const loadStep = async () => {
  loading.value = true
  error.value = ''

  try {
    // Load the track to get all steps
    const trackId = route.params.trackId || route.query.trackId
    if (trackId) {
      const trackResponse = await learningAPI.getLearningPath(trackId)
      allSteps.value = trackResponse.data.steps || []
    }

    // Load current step details
    const response = await learningAPI.getLearningPath(stepId.value)
    currentStep.value = response.data

    // Reset quiz state
    currentQuestionIndex.value = 0
    answerSelected.value = false
    selectedAlternative.value = null
    quizAnswers.value = []

  } catch (err) {
    console.error('Failed to load step:', err)
    error.value = 'Failed to load exercise. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  const trackId = route.params.trackId || route.query.trackId
  if (trackId) {
    router.push({ name: 'Dashboard' })
  } else {
    router.back()
  }
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(currentStep.value.code_snippet)
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const selectAnswer = (alternative) => {
  if (answerSelected.value) return

  answerSelected.value = true
  selectedAlternative.value = alternative

  quizAnswers.value[currentQuestionIndex.value] = {
    question_id: currentQuestion.value.id,
    alternative_id: alternative.id,
    is_correct: alternative.is_correct
  }
}

const getAlternativeClass = (alternative) => {
  if (!answerSelected.value) {
    return 'border-gray-300 bg-white'
  }

  if (alternative.is_correct) {
    return 'border-green-500 bg-green-50'
  }

  if (selectedAlternative.value?.id === alternative.id && !alternative.is_correct) {
    return 'border-red-500 bg-red-50'
  }

  return 'border-gray-300 bg-gray-50 opacity-50'
}

const getCircleClass = (alternative) => {
  if (!answerSelected.value) {
    return 'border-gray-400 text-gray-600'
  }

  if (alternative.is_correct) {
    return 'border-green-600 bg-green-600 text-white'
  }

  if (selectedAlternative.value?.id === alternative.id && !alternative.is_correct) {
    return 'border-red-600 bg-red-600 text-white'
  }

  return 'border-gray-300 text-gray-400'
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    answerSelected.value = !!quizAnswers.value[currentQuestionIndex.value]
    selectedAlternative.value = answerSelected.value ?
      currentQuestion.value.alternatives.find(a => a.id === quizAnswers.value[currentQuestionIndex.value].alternative_id) :
      null
  }
}

const nextQuestionOrComplete = () => {
  if (isLastQuestion.value) {
    completeAndNext()
  } else {
    currentQuestionIndex.value++
    answerSelected.value = !!quizAnswers.value[currentQuestionIndex.value]
    selectedAlternative.value = null
  }
}

const completeAndNext = async () => {
  completing.value = true

  try {
    // Complete the step
    await progressAPI.completeStep(stepId.value)

    // Show celebration
    showCelebration.value = true

    // Refresh user profile to get updated XP
    await authStore.fetchUser()

  } catch (err) {
    console.error('Failed to complete step:', err)
    error.value = 'Failed to complete exercise. Please try again.'
  } finally {
    completing.value = false
  }
}

// Code Challenge Methods
const handleCodeCorrect = ({ output, time }) => {
  codeIsCorrect.value = true
  codeOutput.value = output
  console.log(`Code executed correctly in ${time}ms`)
}

const handleCodeRun = ({ output, time }) => {
  codeAttempts.value++
  codeOutput.value = output
}

const handleCodeError = (err) => {
  codeAttempts.value++
  console.error('Code execution error:', err)
}

const getCodeHints = () => {
  // Return hints based on number of attempts
  if (codeAttempts.value === 0) return []
  if (codeAttempts.value === 1) return ['Check your syntax carefully']
  if (codeAttempts.value === 2) return [
    'Check your syntax carefully',
    'Make sure you\'re using the correct function names'
  ]
  return [
    'Check your syntax carefully',
    'Make sure you\'re using the correct function names',
    'Click "Solution" to see the correct answer'
  ]
}

const continueToNext = () => {
  showCelebration.value = false

  if (hasNextStep.value) {
    // Go to next step
    const currentIndex = allSteps.value.findIndex(s => s.id === stepId.value)
    const nextStep = allSteps.value[currentIndex + 1]

    router.push({
      name: 'StepExercise',
      params: { stepId: nextStep.id, trackId: route.params.trackId }
    })

    // Reload the new step
    loadStep()
  } else {
    // Return to dashboard
    router.push({ name: 'Dashboard' })
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadStep()
})
</script>

<style scoped>
/* Prose styling for lesson content */
:deep(.prose) {
  color: #374151;
}

:deep(.prose h2) {
  color: #111827;
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.prose h3) {
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
}

:deep(.prose p) {
  margin-bottom: 1rem;
  line-height: 1.75;
}

:deep(.prose ul) {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
  list-style-type: disc;
}

:deep(.prose li) {
  margin-bottom: 0.5rem;
}

:deep(.prose code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
  font-family: 'Courier New', monospace;
}

:deep(.prose pre) {
  background-color: #1f2937;
  color: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

:deep(.prose pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

:deep(.prose strong) {
  font-weight: 600;
  color: #111827;
}
</style>
