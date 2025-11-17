<template>
  <div class="quiz-enhanced min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-8 px-4">
    <!-- Progress Header -->
    <div class="max-w-4xl mx-auto mb-8">
      <div class="card p-6">
        <!-- XP Display -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ quizTitle }}</h2>
            <p class="text-gray-600 dark:text-gray-400 mt-1">{{ quizDescription }}</p>
          </div>
          <div class="text-right">
            <div class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ totalPoints }} XP
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ questions.length }} questões
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="relative">
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-out"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
          <div class="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
            <span>Questão {{ currentQuestionIndex + 1 }} de {{ questions.length }}</span>
            <span>{{ progressPercentage }}% completo</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Question -->
    <div class="max-w-4xl mx-auto" v-if="currentQuestion && !showResults">
      <div class="card p-8">
        <!-- Question Header -->
        <div class="flex items-start justify-between mb-6">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <span class="px-3 py-1 rounded-full text-xs font-semibold"
                    :class="difficultyClasses[currentQuestion.difficulty]">
                {{ difficultyLabels[currentQuestion.difficulty] }}
              </span>
              <span class="text-indigo-600 dark:text-indigo-400 font-semibold">
                +{{ currentQuestion.points }} XP
              </span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white leading-relaxed">
              {{ currentQuestion.text }}
            </h3>
          </div>

          <!-- Question Type Icon -->
          <div class="ml-4 text-4xl">
            {{ questionTypeIcons[currentQuestion.question_type] }}
          </div>
        </div>

        <!-- Hint Button -->
        <button
          v-if="currentQuestion.hint && !showHint"
          @click="showHint = true"
          class="mb-4 text-sm text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-2"
        >
          <span>💡</span>
          <span>Ver dica</span>
        </button>

        <!-- Hint Display -->
        <div v-if="showHint && currentQuestion.hint" class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 rounded">
          <p class="text-sm text-yellow-800 dark:text-yellow-200">
            💡 {{ currentQuestion.hint }}
          </p>
        </div>

        <!-- Question Type: Multiple Choice -->
        <div v-if="currentQuestion.question_type === 'multiple_choice'" class="space-y-3">
          <button
            v-for="(choice, index) in currentQuestion.choices"
            :key="choice.id"
            @click="selectAnswer(choice)"
            :disabled="answered"
            class="w-full text-left p-4 rounded-xl border-2 transition-all duration-200"
            :class="getChoiceClasses(choice)"
          >
            <div class="flex items-center gap-3">
              <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-semibold"
                   :class="getChoiceNumberClasses(choice)">
                {{ String.fromCharCode(65 + index) }}
              </div>
              <div class="flex-1 font-medium">{{ choice.text }}</div>
              <div v-if="answered" class="flex-shrink-0 text-2xl">
                {{ choice.is_correct ? '✓' : selectedChoice?.id === choice.id ? '✗' : '' }}
              </div>
            </div>
          </button>
        </div>

        <!-- Question Type: Fill in the Blank -->
        <div v-else-if="currentQuestion.question_type === 'fill_blank'" class="space-y-4">
          <input
            v-model="userAnswer"
            type="text"
            :disabled="answered"
            @keyup.enter="submitAnswer"
            class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white text-lg"
            :class="{ 'border-green-500': answered && isCorrect, 'border-red-500': answered && !isCorrect }"
            placeholder="Digite sua resposta..."
          />
        </div>

        <!-- Question Type: Short Answer -->
        <div v-else-if="currentQuestion.question_type === 'short_answer'" class="space-y-4">
          <textarea
            v-model="userAnswer"
            :disabled="answered"
            rows="4"
            class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white resize-none"
            :class="{ 'border-green-500': answered && isCorrect, 'border-red-500': answered && !isCorrect }"
            :maxlength="currentQuestion.max_answer_length"
            placeholder="Digite sua resposta..."
          ></textarea>
          <div class="text-right text-sm text-gray-500">
            {{ userAnswer.length }} / {{ currentQuestion.max_answer_length }}
          </div>
        </div>

        <!-- Question Type: True/False -->
        <div v-else-if="currentQuestion.question_type === 'true_false'" class="grid grid-cols-2 gap-4">
          <button
            @click="selectTrueFalse(true)"
            :disabled="answered"
            class="p-6 rounded-xl border-2 font-semibold text-lg transition-all duration-200"
            :class="getTrueFalseClasses(true)"
          >
            <div class="text-4xl mb-2">✓</div>
            <div>Verdadeiro</div>
          </button>
          <button
            @click="selectTrueFalse(false)"
            :disabled="answered"
            class="p-6 rounded-xl border-2 font-semibold text-lg transition-all duration-200"
            :class="getTrueFalseClasses(false)"
          >
            <div class="text-4xl mb-2">✗</div>
            <div>Falso</div>
          </button>
        </div>

        <!-- Explanation (shown after answering) -->
        <div v-if="answered && currentQuestion.explanation" class="mt-6 p-4 rounded-xl"
             :class="isCorrect ? 'bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500' : 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500'">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 text-2xl">
              {{ isCorrect ? '🎉' : '📚' }}
            </div>
            <div class="flex-1">
              <h4 class="font-semibold mb-2" :class="isCorrect ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'">
                {{ isCorrect ? 'Correto!' : 'Explicação' }}
              </h4>
              <p class="text-sm" :class="isCorrect ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'">
                {{ currentQuestion.explanation }}
              </p>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-8 flex items-center justify-between">
          <button
            v-if="currentQuestionIndex > 0"
            @click="previousQuestion"
            :disabled="!answered"
            class="btn-secondary flex items-center gap-2"
          >
            <span>←</span>
            <span>Anterior</span>
          </button>
          <div v-else></div>

          <button
            v-if="!answered"
            @click="submitAnswer"
            :disabled="!canSubmit"
            class="btn-primary"
          >
            Confirmar Resposta
          </button>

          <button
            v-else-if="currentQuestionIndex < questions.length - 1"
            @click="nextQuestion"
            class="btn-primary flex items-center gap-2"
          >
            <span>Próxima</span>
            <span>→</span>
          </button>

          <button
            v-else
            @click="finishQuiz"
            class="btn-primary bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
          >
            Finalizar Quiz
          </button>
        </div>
      </div>
    </div>

    <!-- Results Screen -->
    <div v-if="showResults" class="max-w-4xl mx-auto">
      <div class="card p-8 text-center">
        <!-- Celebration Animation -->
        <div class="text-8xl mb-6 animate-bounce">
          {{ scorePercentage >= 80 ? '🎉' : scorePercentage >= 60 ? '👍' : '📚' }}
        </div>

        <!-- Score -->
        <h2 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          {{ scorePercentage >= 80 ? 'Excelente!' : scorePercentage >= 60 ? 'Bom trabalho!' : 'Continue praticando!' }}
        </h2>
        <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
          Você acertou {{ correctAnswers }} de {{ questions.length }} questões
        </p>

        <!-- XP Earned -->
        <div class="mb-8 p-6 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl text-white">
          <div class="text-5xl font-bold mb-2">+{{ earnedXP }} XP</div>
          <div class="text-lg opacity-90">XP conquistado neste quiz!</div>
        </div>

        <!-- Score Breakdown -->
        <div class="grid grid-cols-3 gap-4 mb-8">
          <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl">
            <div class="text-3xl font-bold text-green-600 dark:text-green-400">{{ correctAnswers }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Corretas</div>
          </div>
          <div class="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl">
            <div class="text-3xl font-bold text-red-600 dark:text-red-400">{{ wrongAnswers }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Erradas</div>
          </div>
          <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ scorePercentage }}%</div>
            <div class="text-sm text-gray-600 dark:text-gray-400">Precisão</div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 justify-center">
          <button @click="reviewAnswers" class="btn-secondary">
            Revisar Respostas
          </button>
          <button @click="$emit('quiz-completed', { score: scorePercentage, xp: earnedXP })" class="btn-primary">
            Continuar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  quizTitle: {
    type: String,
    required: true
  },
  quizDescription: {
    type: String,
    default: ''
  },
  questions: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['quiz-completed'])

// State
const currentQuestionIndex = ref(0)
const answers = ref([])
const answered = ref(false)
const selectedChoice = ref(null)
const userAnswer = ref('')
const trueFalseAnswer = ref(null)
const showHint = ref(false)
const showResults = ref(false)

// Computed
const currentQuestion = computed(() => props.questions[currentQuestionIndex.value])

const progressPercentage = computed(() => {
  return Math.round((currentQuestionIndex.value / props.questions.length) * 100)
})

const totalPoints = computed(() => {
  return props.questions.reduce((sum, q) => sum + (q.points || 10), 0)
})

const isCorrect = computed(() => {
  if (!answered.value) return false

  const question = currentQuestion.value
  const answer = answers.value[currentQuestionIndex.value]

  return answer?.correct || false
})

const canSubmit = computed(() => {
  const question = currentQuestion.value

  if (question.question_type === 'multiple_choice') {
    return selectedChoice.value !== null
  } else if (question.question_type === 'fill_blank' || question.question_type === 'short_answer') {
    return userAnswer.value.trim().length > 0
  } else if (question.question_type === 'true_false') {
    return trueFalseAnswer.value !== null
  }

  return false
})

const correctAnswers = computed(() => {
  return answers.value.filter(a => a.correct).length
})

const wrongAnswers = computed(() => {
  return answers.value.filter(a => !a.correct).length
})

const scorePercentage = computed(() => {
  if (answers.value.length === 0) return 0
  return Math.round((correctAnswers.value / answers.value.length) * 100)
})

const earnedXP = computed(() => {
  return answers.value.reduce((sum, answer, index) => {
    return sum + (answer.correct ? (props.questions[index].points || 10) : 0)
  }, 0)
})

// Constants
const difficultyClasses = {
  easy: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  hard: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
}

const difficultyLabels = {
  easy: 'Fácil',
  medium: 'Médio',
  hard: 'Difícil'
}

const questionTypeIcons = {
  multiple_choice: '☑️',
  fill_blank: '✏️',
  short_answer: '📝',
  true_false: '❓',
  reorder: '🔢',
  matching: '🔗'
}

// Methods
function selectAnswer(choice) {
  if (answered.value) return
  selectedChoice.value = choice
}

function selectTrueFalse(value) {
  if (answered.value) return
  trueFalseAnswer.value = value
}

function submitAnswer() {
  if (!canSubmit.value || answered.value) return

  const question = currentQuestion.value
  let correct = false
  let userResponse = null

  if (question.question_type === 'multiple_choice') {
    correct = selectedChoice.value?.is_correct || false
    userResponse = selectedChoice.value?.id
  } else if (question.question_type === 'fill_blank') {
    correct = validateTextAnswer(userAnswer.value, question.correct_answer, question.validation_type)
    userResponse = userAnswer.value
  } else if (question.question_type === 'short_answer') {
    correct = validateTextAnswer(userAnswer.value, question.correct_answer, question.validation_type)
    userResponse = userAnswer.value
  } else if (question.question_type === 'true_false') {
    correct = trueFalseAnswer.value === (question.correct_answer === 'true')
    userResponse = trueFalseAnswer.value
  }

  answers.value[currentQuestionIndex.value] = {
    question_id: question.id,
    correct,
    user_response: userResponse
  }

  answered.value = true
}

function validateTextAnswer(userAnswer, correctAnswer, validationType) {
  const user = userAnswer.trim()
  const correct = correctAnswer.trim()

  switch (validationType) {
    case 'exact':
      return user === correct
    case 'case_insensitive':
      return user.toLowerCase() === correct.toLowerCase()
    case 'contains':
      // Check if user answer contains any of the keywords (separated by |)
      const keywords = correct.toLowerCase().split('|')
      const userLower = user.toLowerCase()
      return keywords.some(keyword => userLower.includes(keyword.trim()))
    case 'regex':
      const regex = new RegExp(correct)
      return regex.test(user)
    default:
      return user.toLowerCase() === correct.toLowerCase()
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < props.questions.length - 1) {
    currentQuestionIndex.value++
    resetQuestionState()
  }
}

function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    resetQuestionState()
  }
}

function resetQuestionState() {
  answered.value = answers.value[currentQuestionIndex.value] !== undefined
  selectedChoice.value = null
  userAnswer.value = ''
  trueFalseAnswer.value = null
  showHint.value = false
}

function finishQuiz() {
  showResults.value = true
}

function reviewAnswers() {
  showResults.value = false
  currentQuestionIndex.value = 0
  resetQuestionState()
}

function getChoiceClasses(choice) {
  if (!answered.value) {
    return selectedChoice.value?.id === choice.id
      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
      : 'border-gray-300 dark:border-gray-600 hover:border-indigo-300 dark:hover:border-indigo-700'
  }

  if (choice.is_correct) {
    return 'border-green-500 bg-green-50 dark:bg-green-900/30'
  }

  if (selectedChoice.value?.id === choice.id && !choice.is_correct) {
    return 'border-red-500 bg-red-50 dark:bg-red-900/30'
  }

  return 'border-gray-300 dark:border-gray-600 opacity-50'
}

function getChoiceNumberClasses(choice) {
  if (!answered.value) {
    return selectedChoice.value?.id === choice.id
      ? 'bg-indigo-500 text-white'
      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
  }

  if (choice.is_correct) {
    return 'bg-green-500 text-white'
  }

  if (selectedChoice.value?.id === choice.id) {
    return 'bg-red-500 text-white'
  }

  return 'bg-gray-200 dark:bg-gray-700 text-gray-400'
}

function getTrueFalseClasses(value) {
  const correctValue = currentQuestion.value.correct_answer === 'true'

  if (!answered.value) {
    return trueFalseAnswer.value === value
      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
      : 'border-gray-300 dark:border-gray-600 hover:border-indigo-300'
  }

  if (value === correctValue) {
    return 'border-green-500 bg-green-50 dark:bg-green-900/30'
  }

  if (trueFalseAnswer.value === value) {
    return 'border-red-500 bg-red-50 dark:bg-red-900/30'
  }

  return 'border-gray-300 dark:border-gray-600 opacity-50'
}
</script>

<style scoped>
.card {
  @apply bg-white dark:bg-gray-800 rounded-2xl shadow-lg;
}

.btn-primary {
  @apply px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-semibold rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
