import { defineStore } from 'pinia'
import { learningAPI, progressAPI } from '@/services/api'

export const useLearningStore = defineStore('learning', {
  state: () => ({
    learningPaths: [],
    currentStep: null,
    userProgress: [],
    progressSummary: null,
    loading: false,
    error: null,
  }),

  getters: {
    allAreas: (state) => state.learningPaths,

    getStepById: (state) => (stepId) => {
      for (const area of state.learningPaths) {
        for (const topic of area.topics || []) {
          for (const track of topic.tracks || []) {
            const step = track.steps?.find(s => s.id === parseInt(stepId))
            if (step) return step
          }
        }
      }
      return null
    },

    isStepCompleted: (state) => (stepId) => {
      return state.userProgress.some(
        p => p.step.id === parseInt(stepId) && p.status === 'completed'
      )
    },

    getProgressForStep: (state) => (stepId) => {
      return state.userProgress.find(p => p.step.id === parseInt(stepId))
    },
  },

  actions: {
    async fetchLearningPaths() {
      this.loading = true
      this.error = null

      try {
        const response = await learningAPI.getLearningPaths()
        this.learningPaths = response.data.results || response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch learning paths'
        console.error('Error fetching learning paths:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchUserProgress() {
      this.loading = true
      this.error = null

      try {
        const response = await progressAPI.getMyProgress()
        this.userProgress = response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch progress'
        console.error('Error fetching user progress:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchProgressSummary() {
      this.loading = true
      this.error = null

      try {
        const response = await progressAPI.getProgressSummary()
        this.progressSummary = response.data
      } catch (error) {
        this.error = error.response?.data || 'Failed to fetch progress summary'
        console.error('Error fetching progress summary:', error)
      } finally {
        this.loading = false
      }
    },

    async completeStep(stepId) {
      try {
        const response = await progressAPI.completeStep(stepId)

        // Update local progress
        const existingProgressIndex = this.userProgress.findIndex(
          p => p.step?.id === parseInt(stepId)
        )

        if (existingProgressIndex !== -1) {
          this.userProgress[existingProgressIndex] = response.data.progress
        } else {
          this.userProgress.push(response.data.progress)
        }

        // Refresh progress summary
        await this.fetchProgressSummary()

        return { success: true }
      } catch (error) {
        this.error = error.response?.data || 'Failed to complete step'
        return { success: false, error: this.error }
      }
    },

    setCurrentStep(step) {
      this.currentStep = step
    },
  },
})
