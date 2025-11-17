<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8 animate-fade-in">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🤖 AI Content Generator</h1>
      <p class="text-gray-600">Generate lessons and quiz questions using AI providers</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Generation Form -->
      <div class="lg:col-span-2">
        <div class="card animate-scale-in">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Generate Content</h2>

          <form @submit.prevent="handleGenerate" class="space-y-4">
            <!-- Content Type Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Content Type
              </label>
              <div class="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  @click="contentType = 'lesson'"
                  :class="[
                    'px-4 py-3 rounded-lg border-2 font-medium transition-all',
                    contentType === 'lesson'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  ]"
                >
                  📚 Lesson
                </button>
                <button
                  type="button"
                  @click="contentType = 'quiz'"
                  :class="[
                    'px-4 py-3 rounded-lg border-2 font-medium transition-all',
                    contentType === 'quiz'
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  ]"
                >
                  ❓ Quiz
                </button>
              </div>
            </div>

            <!-- AI Provider Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                AI Provider
              </label>
              <select v-model="selectedProvider" class="input" required>
                <option value="">Select a provider...</option>
                <option
                  v-for="provider in providers"
                  :key="provider.id"
                  :value="provider.id"
                >
                  {{ provider.name }} ({{ provider.provider_type_display }})
                </option>
              </select>
            </div>

            <!-- Topic Input -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Topic
              </label>
              <input
                v-model="topic"
                type="text"
                class="input"
                placeholder="e.g., Python Functions, Introduction to Algebra"
                required
              />
            </div>

            <!-- Difficulty Level -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Difficulty Level
              </label>
              <select v-model="difficulty" class="input">
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <!-- Language -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <select v-model="language" class="input">
                <option value="Portuguese">Portuguese</option>
                <option value="English">English</option>
                <option value="Spanish">Spanish</option>
              </select>
            </div>

            <!-- Number of Questions (for quiz only) -->
            <div v-if="contentType === 'quiz'">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Number of Questions
              </label>
              <input
                v-model.number="numQuestions"
                type="number"
                min="1"
                max="20"
                class="input"
              />
            </div>

            <!-- Additional Context (for lesson only) -->
            <div v-if="contentType === 'lesson'">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                v-model="additionalContext"
                rows="3"
                class="input"
                placeholder="Any specific aspects to focus on..."
              ></textarea>
            </div>

            <!-- Generate Button -->
            <button
              type="submit"
              :disabled="isGenerating"
              class="btn btn-primary w-full flex items-center justify-center space-x-2"
            >
              <span v-if="isGenerating" class="inline-block animate-spin">⚙️</span>
              <span v-else>✨</span>
              <span>{{ isGenerating ? 'Generating...' : 'Generate Content' }}</span>
            </button>
          </form>

          <!-- Error Message -->
          <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg animate-scale-in">
            <p class="text-red-800 text-sm">❌ {{ error }}</p>
          </div>
        </div>

        <!-- Generated Content Display -->
        <div v-if="generatedContent" class="card mt-6 animate-slide-up">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold text-gray-900">Generated Content</h2>
            <span class="text-sm text-gray-500">
              ⏱️ {{ generatedContent.generation_time.toFixed(2) }}s |
              🎫 {{ generatedContent.tokens_used }} tokens
            </span>
          </div>

          <!-- Content Preview -->
          <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre class="whitespace-pre-wrap text-sm text-gray-800">{{ generatedContent.generated_text }}</pre>
          </div>

          <!-- Parsed Content (if available) -->
          <div v-if="generatedContent.parsed_content && Object.keys(generatedContent.parsed_content).length > 1" class="mt-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-2">Structured Data:</h3>
            <div class="bg-white rounded-lg p-3 border border-gray-200">
              <pre class="text-xs text-gray-700">{{ JSON.stringify(generatedContent.parsed_content, null, 2) }}</pre>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-4 flex space-x-3">
            <button
              @click="copyToClipboard"
              class="btn btn-secondary flex-1"
            >
              📋 Copy to Clipboard
            </button>
            <button
              @click="generatedContent = null"
              class="btn btn-secondary"
            >
              ✖️ Close
            </button>
          </div>
        </div>
      </div>

      <!-- Sidebar: Recent Generations -->
      <div class="lg:col-span-1">
        <div class="card animate-slide-up" style="animation-delay: 0.2s">
          <h2 class="text-lg font-bold text-gray-900 mb-4">📜 Recent Generations</h2>

          <div v-if="loadingHistory" class="text-center py-8 text-gray-500">
            <div class="inline-block animate-spin text-2xl">⚙️</div>
            <p class="text-sm mt-2">Loading history...</p>
          </div>

          <div v-else-if="history.length === 0" class="text-center py-8 text-gray-500">
            <p class="text-sm">No generations yet</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="item in history"
              :key="item.id"
              @click="viewGeneration(item.id)"
              class="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer border border-gray-200"
            >
              <div class="flex items-start justify-between mb-1">
                <span class="text-xs font-semibold text-gray-700">
                  {{ item.content_type || 'Content' }}
                </span>
                <span v-if="item.was_successful" class="text-green-600 text-xs">✓</span>
                <span v-else class="text-red-600 text-xs">✗</span>
              </div>
              <p class="text-xs text-gray-600 line-clamp-2">{{ item.preview }}</p>
              <div class="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>{{ item.provider }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </div>

          <button
            v-if="history.length > 0"
            @click="refreshHistory"
            class="btn btn-secondary w-full mt-4 text-sm"
          >
            🔄 Refresh
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { aiAPI } from '@/services/api'

// ============================================================================
// State
// ============================================================================

const providers = ref([])
const history = ref([])
const generatedContent = ref(null)

const contentType = ref('lesson')
const selectedProvider = ref('')
const topic = ref('')
const difficulty = ref('intermediate')
const language = ref('Portuguese')
const numQuestions = ref(5)
const additionalContext = ref('')

const isGenerating = ref(false)
const loadingHistory = ref(false)
const error = ref('')

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await loadProviders()
  await loadHistory()
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Load available AI providers
 */
const loadProviders = async () => {
  try {
    const response = await aiAPI.getProviders()
    providers.value = response.data.providers
  } catch (err) {
    console.error('Failed to load providers:', err)
    error.value = 'Failed to load AI providers'
  }
}

/**
 * Load generation history
 */
const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await aiAPI.getHistory(10)
    history.value = response.data.history
  } catch (err) {
    console.error('Failed to load history:', err)
  } finally {
    loadingHistory.value = false
  }
}

/**
 * Refresh generation history
 */
const refreshHistory = async () => {
  await loadHistory()
}

/**
 * Handle content generation
 */
const handleGenerate = async () => {
  if (!selectedProvider.value || !topic.value) {
    error.value = 'Please select a provider and enter a topic'
    return
  }

  isGenerating.value = true
  error.value = ''
  generatedContent.value = null

  try {
    let response

    if (contentType.value === 'lesson') {
      response = await aiAPI.generateLesson({
        provider_id: selectedProvider.value,
        topic: topic.value,
        difficulty: difficulty.value,
        language: language.value,
        additional_context: additionalContext.value,
      })
    } else {
      response = await aiAPI.generateQuiz({
        provider_id: selectedProvider.value,
        topic: topic.value,
        difficulty: difficulty.value,
        language: language.value,
        num_questions: numQuestions.value,
      })
    }

    generatedContent.value = response.data

    // Refresh history after successful generation
    await loadHistory()

  } catch (err) {
    console.error('Generation failed:', err)
    error.value = err.response?.data?.error || 'Failed to generate content. Please try again.'
  } finally {
    isGenerating.value = false
  }
}

/**
 * View details of a specific generation
 */
const viewGeneration = async (generationId) => {
  try {
    const response = await aiAPI.getGenerationDetail(generationId)
    generatedContent.value = response.data
  } catch (err) {
    console.error('Failed to load generation:', err)
    error.value = 'Failed to load generation details'
  }
}

/**
 * Copy generated content to clipboard
 */
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedContent.value.generated_text)
    alert('✅ Copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
    alert('❌ Failed to copy to clipboard')
  }
}

/**
 * Format date for display
 */
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
