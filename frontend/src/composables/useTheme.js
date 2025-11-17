/**
 * Theme Management Composable
 *
 * Manages dark/light mode with localStorage persistence
 * and system preference detection
 */

import { ref, watch, onMounted } from 'vue'

const isDark = ref(false)
const STORAGE_KEY = 'learnhub-theme'

export function useTheme() {
  /**
   * Initialize theme from localStorage or system preference
   */
  const initTheme = () => {
    // Check localStorage first
    const stored = localStorage.getItem(STORAGE_KEY)

    if (stored) {
      isDark.value = stored === 'dark'
    } else {
      // Check system preference
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }

    applyTheme()
  }

  /**
   * Apply theme to document
   */
  const applyTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  /**
   * Toggle between dark and light mode
   */
  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    applyTheme()
  }

  /**
   * Set specific theme
   */
  const setTheme = (theme) => {
    isDark.value = theme === 'dark'
    localStorage.setItem(STORAGE_KEY, theme)
    applyTheme()
  }

  /**
   * Listen for system theme changes
   */
  const listenToSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    mediaQuery.addEventListener('change', (e) => {
      // Only apply if user hasn't manually set a preference
      if (!localStorage.getItem(STORAGE_KEY)) {
        isDark.value = e.matches
        applyTheme()
      }
    })
  }

  // Watch for changes
  watch(isDark, () => {
    applyTheme()
  })

  return {
    isDark,
    initTheme,
    toggleTheme,
    setTheme,
    listenToSystemTheme
  }
}
