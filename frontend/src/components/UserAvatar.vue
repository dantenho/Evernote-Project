<template>
  <div class="relative inline-block">
    <!-- Avatar Display -->
    <button
      v-if="!editable"
      class="flex items-center justify-center rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-primary-500"
      :class="sizeClasses"
      :style="{ backgroundColor: bgColor }"
    >
      <!-- URL Avatar -->
      <img
        v-if="avatarData.type === 'url'"
        :src="avatarData.value"
        :alt="alt"
        class="w-full h-full rounded-full object-cover"
      />
      <!-- Preset Emoji Avatar -->
      <span
        v-else
        class="text-center leading-none"
        :class="emojiSizeClass"
      >
        {{ avatarData.value }}
      </span>
    </button>

    <!-- Editable Avatar with Selector -->
    <div v-else>
      <button
        @click="showSelector = !showSelector"
        class="flex items-center justify-center rounded-full transition-all hover:ring-2 hover:ring-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-600 cursor-pointer"
        :class="sizeClasses"
        :style="{ backgroundColor: bgColor }"
        :title="'Click to change avatar'"
      >
        <!-- URL Avatar -->
        <img
          v-if="avatarData.type === 'url'"
          :src="avatarData.value"
          :alt="alt"
          class="w-full h-full rounded-full object-cover"
        />
        <!-- Preset Emoji Avatar -->
        <span
          v-else
          class="text-center leading-none"
          :class="emojiSizeClass"
        >
          {{ avatarData.value }}
        </span>

        <!-- Edit Indicator -->
        <div class="absolute bottom-0 right-0 bg-primary-500 rounded-full p-1 shadow-lg">
          <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </div>
      </button>

      <!-- Avatar Selector Modal -->
      <div
        v-if="showSelector"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in"
        @click="showSelector = false"
      >
        <div
          class="bg-white dark:bg-dark-card rounded-xl p-6 max-w-md w-full mx-4 animate-scale-in"
          @click.stop
        >
          <h3 class="text-xl font-bold text-gray-900 dark:text-dark-primary mb-4">
            Choose Your Avatar
          </h3>

          <!-- Preset Avatars Grid -->
          <div class="mb-6">
            <h4 class="text-sm font-semibold text-gray-700 dark:text-dark-secondary mb-3">
              Preset Avatars
            </h4>
            <div class="grid grid-cols-6 gap-3">
              <button
                v-for="(emoji, index) in presetAvatars"
                :key="index"
                @click="selectPreset(emoji)"
                class="w-12 h-12 flex items-center justify-center text-3xl rounded-full hover:bg-gray-100 dark:hover:bg-dark-hover transition-all hover:scale-110"
                :class="{ 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/30': avatarData.value === emoji }"
                :title="`Select ${emoji}`"
              >
                {{ emoji }}
              </button>
            </div>
          </div>

          <!-- Custom URL Input -->
          <div class="mb-6">
            <h4 class="text-sm font-semibold text-gray-700 dark:text-dark-secondary mb-2">
              Custom Avatar URL
            </h4>
            <div class="flex space-x-2">
              <input
                v-model="customUrl"
                type="url"
                placeholder="https://example.com/avatar.jpg"
                class="input flex-1 text-sm"
              />
              <button
                @click="selectCustomUrl"
                :disabled="!isValidUrl(customUrl)"
                class="btn btn-primary px-4"
                :class="{ 'opacity-50 cursor-not-allowed': !isValidUrl(customUrl) }"
              >
                Set
              </button>
            </div>
            <p class="text-xs text-gray-500 dark:text-dark-muted mt-1">
              Enter a URL to an image (JPG, PNG, GIF)
            </p>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3">
            <button
              @click="showSelector = false"
              class="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              @click="saveAvatar"
              class="btn btn-primary"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  avatarData: {
    type: Object,
    default: () => ({ type: 'preset', value: '👨‍💻' })
  },
  alt: {
    type: String,
    default: 'User Avatar'
  },
  size: {
    type: String,
    default: 'md', // xs, sm, md, lg, xl
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  editable: {
    type: Boolean,
    default: false
  },
  bgColor: {
    type: String,
    default: '#e5e7eb' // gray-200
  }
})

// Emits
const emit = defineEmits(['update:avatar'])

// State
const showSelector = ref(false)
const customUrl = ref('')
const selectedAvatar = ref(props.avatarData)

// Preset avatars (same as in Django model)
const presetAvatars = [
  '👨‍💻', '👩‍💻', '🧑‍💻', '👨‍🎓', '👩‍🎓', '🧑‍🎓',
  '🦸‍♂️', '🦸‍♀️', '🦸', '🧙‍♂️', '🧙‍♀️', '🧙',
  '🐱', '🐶', '🦊', '🐼', '🐨', '🦁',
  '🚀', '⭐', '🌟', '💎', '🏆', '🎯',
]

// Computed
const sizeClasses = computed(() => {
  const sizes = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  }
  return sizes[props.size] || sizes.md
})

const emojiSizeClass = computed(() => {
  const sizes = {
    xs: 'text-sm',
    sm: 'text-base',
    md: 'text-2xl',
    lg: 'text-4xl',
    xl: 'text-6xl'
  }
  return sizes[props.size] || sizes.md
})

// Methods
const isValidUrl = (url) => {
  if (!url) return false
  try {
    new URL(url)
    return url.match(/\.(jpg|jpeg|png|gif|webp)$/i) !== null
  } catch {
    return false
  }
}

const selectPreset = (emoji) => {
  selectedAvatar.value = {
    type: 'preset',
    value: emoji
  }
}

const selectCustomUrl = () => {
  if (isValidUrl(customUrl.value)) {
    selectedAvatar.value = {
      type: 'url',
      value: customUrl.value
    }
    customUrl.value = ''
  }
}

const saveAvatar = () => {
  emit('update:avatar', selectedAvatar.value)
  showSelector.value = false
}
</script>
