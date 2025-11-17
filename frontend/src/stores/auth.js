import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    currentUser: (state) => state.user,
  },

  actions: {
    async register(userData) {
      this.loading = true
      this.error = null

      try {
        const response = await authAPI.register(userData)
        const { user, access, refresh } = response.data

        this.user = user
        this.accessToken = access
        this.refreshToken = refresh

        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        return { success: true }
      } catch (error) {
        this.error = error.response?.data || 'Registration failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await authAPI.login(credentials)
        const { access, refresh } = response.data

        this.accessToken = access
        this.refreshToken = refresh

        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        // Fetch user profile
        await this.fetchProfile()

        return { success: true }
      } catch (error) {
        this.error = error.response?.data || 'Login failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        if (this.refreshToken) {
          await authAPI.logout(this.refreshToken)
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.accessToken = null
        this.refreshToken = null

        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    },

    async fetchProfile() {
      try {
        const response = await authAPI.getProfile()
        this.user = response.data
      } catch (error) {
        console.error('Failed to fetch profile:', error)
        this.logout()
      }
    },

    async updateProfile(data) {
      this.loading = true
      this.error = null

      try {
        const response = await authAPI.updateProfile(data)
        this.user = response.data
        return { success: true }
      } catch (error) {
        this.error = error.response?.data || 'Update failed'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    async initAuth() {
      if (this.accessToken) {
        await this.fetchProfile()
      }
    },
  },
})
