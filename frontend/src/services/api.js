import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        localStorage.setItem('access_token', access)

        originalRequest.headers.Authorization = `Bearer ${access}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh token failed, logout user
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register(userData) {
    return apiClient.post('/auth/register/', userData)
  },
  login(credentials) {
    return apiClient.post('/auth/login/', credentials)
  },
  logout(refreshToken) {
    return apiClient.post('/auth/logout/', { refresh: refreshToken })
  },
  getProfile() {
    return apiClient.get('/auth/profile/')
  },
  updateProfile(data) {
    return apiClient.patch('/auth/profile/', data)
  },
}

// Learning API
export const learningAPI = {
  getLearningPaths() {
    return apiClient.get('/learning-paths/')
  },
  getLearningPath(id) {
    return apiClient.get(`/learning-paths/${id}/`)
  },
}

// Progress API
export const progressAPI = {
  getMyProgress() {
    return apiClient.get('/my-progress/')
  },
  getProgressSummary() {
    return apiClient.get('/progress/summary/')
  },
  completeStep(stepId) {
    return apiClient.post(`/steps/${stepId}/complete/`)
  },
  createProgress(data) {
    return apiClient.post('/progress/', data)
  },
  updateProgress(progressId, data) {
    return apiClient.patch(`/progress/${progressId}/`, data)
  },
}

export default apiClient
