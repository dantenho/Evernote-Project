<template>
  <div class="progress-tracker">
    <!-- Topic Progress Overview -->
    <div class="card p-6 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ topic.title }}
        </h3>
        <div v-if="topic.is_completed" class="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 rounded-full">
          <span class="text-2xl">🏆</span>
          <span class="font-semibold text-green-800 dark:text-green-300">Completado!</span>
        </div>
      </div>

      <!-- Overall Progress Bar -->
      <div class="mb-6">
        <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Progresso Geral</span>
          <span>{{ topic.completed_tracks }} / {{ topic.total_tracks }} trilhas</span>
        </div>
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden relative">
          <div
            class="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-1000 ease-out"
            :style="{ width: `${topic.percentage}%` }"
          >
            <div class="absolute inset-0 bg-white/20 animate-shimmer"></div>
          </div>
        </div>
        <div class="text-right mt-1 text-sm font-semibold text-gray-700 dark:text-gray-300">
          {{ topic.percentage }}%
        </div>
      </div>

      <!-- Bonus XP Info -->
      <div class="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-xl border-2 border-dashed border-purple-300 dark:border-purple-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="text-3xl">🎁</span>
            <div>
              <div class="font-semibold text-gray-900 dark:text-white">Bônus de Completamento</div>
              <div class="text-sm text-gray-600 dark:text-gray-400">
                Complete todas as trilhas para ganhar
              </div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-3xl font-bold text-purple-600 dark:text-purple-400">
              +{{ topic.bonus_xp_reward }} XP
            </div>
            <div v-if="!topic.is_completed" class="text-xs text-gray-500 dark:text-gray-400">
              Faltam {{ topic.total_tracks - topic.completed_tracks }} trilhas
            </div>
            <div v-else class="text-xs text-green-600 dark:text-green-400 font-semibold">
              ✓ Conquistado!
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Track List -->
    <div class="space-y-4">
      <div
        v-for="(track, index) in topic.tracks"
        :key="track.track_id"
        class="card p-6 transition-all duration-300 hover:shadow-xl"
        :class="{ 'opacity-75': !track.completed }"
      >
        <div class="flex items-start gap-4">
          <!-- Track Number -->
          <div class="flex-shrink-0">
            <div
              class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg"
              :class="trackNumberClasses(track)"
            >
              {{ track.completed ? '✓' : index + 1 }}
            </div>
          </div>

          <!-- Track Info -->
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ track.title }}
              </h4>
              <div class="flex items-center gap-2">
                <span class="text-indigo-600 dark:text-indigo-400 font-semibold">
                  +{{ track.xp_reward }} XP
                </span>
              </div>
            </div>

            <!-- Track Progress -->
            <div class="mb-3">
              <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>{{ track.completed_steps }} / {{ track.total_steps }} passos</span>
                <span>{{ track.percentage }}%</span>
              </div>
              <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div
                  class="h-full transition-all duration-500"
                  :class="track.completed ? 'bg-green-500' : 'bg-indigo-500'"
                  :style="{ width: `${track.percentage}%` }"
                ></div>
              </div>
            </div>

            <!-- Action Button -->
            <div class="flex items-center justify-between">
              <button
                v-if="!track.completed"
                @click="$emit('start-track', track.track_id)"
                class="btn-sm btn-primary"
              >
                {{ track.percentage > 0 ? 'Continuar' : 'Começar' }}
              </button>
              <div v-else class="flex items-center gap-2 text-green-600 dark:text-green-400">
                <span>✓</span>
                <span class="font-semibold">Completado</span>
              </div>

              <!-- Completed At -->
              <div v-if="track.completed" class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(track.completed_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Completion Celebration Modal -->
    <div
      v-if="showCelebration"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      @click="closeCelebration"
    >
      <div
        class="card p-8 max-w-lg w-full mx-4 relative overflow-hidden"
        @click.stop
      >
        <!-- Confetti Animation -->
        <div class="absolute inset-0 pointer-events-none">
          <div v-for="i in 50" :key="i" class="confetti" :style="confettiStyle(i)"></div>
        </div>

        <!-- Content -->
        <div class="relative z-10 text-center">
          <!-- Trophy -->
          <div class="text-8xl mb-6 animate-bounce">
            {{ celebrationType === 'topic' ? '🏆' : '⭐' }}
          </div>

          <!-- Title -->
          <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            {{ celebrationType === 'topic' ? 'Tópico Completado!' : 'Trilha Completada!' }}
          </h2>

          <!-- XP Display -->
          <div class="mb-6">
            <div class="text-6xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 text-transparent bg-clip-text mb-2">
              +{{ celebrationXP }} XP
            </div>
            <div v-if="celebrationType === 'topic'" class="text-lg text-purple-600 dark:text-purple-400 font-semibold">
              Bônus de Completamento do Tópico!
            </div>
          </div>

          <!-- Message -->
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            {{ celebrationMessage }}
          </p>

          <!-- New Rank -->
          <div v-if="leveledUp" class="mb-6 p-4 bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-xl">
            <div class="flex items-center justify-center gap-3">
              <span class="text-3xl">🎖️</span>
              <div>
                <div class="font-semibold text-gray-900 dark:text-white">Novo Rank Desbloqueado!</div>
                <div class="text-lg font-bold text-orange-600 dark:text-orange-400">{{ newRank }}</div>
              </div>
            </div>
          </div>

          <!-- Action Button -->
          <button
            @click="closeCelebration"
            class="btn-primary w-full"
          >
            Continuar Aprendendo
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  topic: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['start-track', 'track-completed', 'topic-completed'])

// State
const showCelebration = ref(false)
const celebrationType = ref('track') // 'track' or 'topic'
const celebrationXP = ref(0)
const celebrationMessage = ref('')
const leveledUp = ref(false)
const newRank = ref('')

// Methods
function trackNumberClasses(track) {
  if (track.completed) {
    return 'bg-green-500 text-white'
  }
  if (track.percentage > 0) {
    return 'bg-indigo-500 text-white'
  }
  return 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short'
  })
}

function showTrackCelebration(xp) {
  celebrationType.value = 'track'
  celebrationXP.value = xp
  celebrationMessage.value = 'Parabéns! Você completou esta trilha com sucesso!'
  showCelebration.value = true
}

function showTopicCelebration(xp, rank = null) {
  celebrationType.value = 'topic'
  celebrationXP.value = xp
  celebrationMessage.value = 'Incrível! Você dominou completamente este tópico!'

  if (rank) {
    leveledUp.value = true
    newRank.value = rank
  }

  showCelebration.value = true
}

function closeCelebration() {
  showCelebration.value = false
  leveledUp.value = false
  newRank.value = ''
}

function confettiStyle(index) {
  const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
  const left = Math.random() * 100
  const animationDuration = 2 + Math.random() * 3
  const delay = Math.random() * 2

  return {
    left: `${left}%`,
    animationDuration: `${animationDuration}s`,
    animationDelay: `${delay}s`,
    backgroundColor: colors[index % colors.length]
  }
}

// Expose methods for parent
defineExpose({
  showTrackCelebration,
  showTopicCelebration
})
</script>

<style scoped>
.card {
  @apply bg-white dark:bg-gray-800 rounded-2xl shadow-lg;
}

.btn-primary {
  @apply px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold rounded-xl hover:from-indigo-600 hover:to-purple-600 transition-all duration-200 shadow-md hover:shadow-lg;
}

.btn-sm {
  @apply px-4 py-2 text-sm;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-100vh) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) rotate(720deg);
    opacity: 0;
  }
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  top: -10px;
  animation: confetti-fall linear infinite;
  opacity: 0.8;
}
</style>
