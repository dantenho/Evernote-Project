/**
 * API Service Module
 *
 * Centralized HTTP client for all API communications.
 * Features:
 * - Automatic JWT token management and refresh
 * - Request/response interceptors for auth and error handling
 * - Retry logic for failed requests
 * - Request cancellation support
 * - Development logging
 */

import axios from 'axios'

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const REQUEST_TIMEOUT = 30000 // 30 seconds
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second base delay

// Development mode detection
const isDevelopment = import.meta.env.MODE === 'development'

// ============================================================================
// Axios Instance Configuration
// ============================================================================

/**
 * Create configured axios instance with default settings
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Check if error is retryable (network error or 5xx server error)
 *
 * @param {Error} error - Axios error object
 * @returns {boolean} True if request should be retried
 */
const isRetryableError = (error) => {
  if (!error.response) {
    // Network error (no response received)
    return true
  }

  const status = error.response.status
  // Retry on server errors (500-599) but not on client errors (400-499)
  return status >= 500 && status < 600
}

/**
 * Calculate exponential backoff delay
 *
 * @param {number} retryCount - Current retry attempt number
 * @returns {number} Delay in milliseconds
 */
const getRetryDelay = (retryCount) => {
  return RETRY_DELAY * Math.pow(2, retryCount)
}

/**
 * Sleep for specified milliseconds
 *
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Log API request in development mode
 *
 * @param {object} config - Axios request config
 */
const logRequest = (config) => {
  if (isDevelopment) {
    console.log(
      `%c[API Request] ${config.method.toUpperCase()} ${config.url}`,
      'color: #2563eb; font-weight: bold',
      config.data || ''
    )
  }
}

/**
 * Log API response in development mode
 *
 * @param {object} response - Axios response object
 */
const logResponse = (response) => {
  if (isDevelopment) {
    console.log(
      `%c[API Response] ${response.status} ${response.config.url}`,
      'color: #16a34a; font-weight: bold',
      response.data
    )
  }
}

/**
 * Log API error in development mode
 *
 * @param {Error} error - Axios error object
 */
const logError = (error) => {
  if (isDevelopment) {
    const status = error.response?.status || 'Network Error'
    const url = error.config?.url || 'Unknown'
    console.error(
      `%c[API Error] ${status} ${url}`,
      'color: #dc2626; font-weight: bold',
      error.response?.data || error.message
    )
  }
}

// ============================================================================
// Request Interceptor
// ============================================================================

/**
 * Add authentication token to all requests
 */
apiClient.interceptors.request.use(
  (config) => {
    // Add JWT access token to authorization header
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Initialize retry count
    config.retryCount = config.retryCount || 0

    // Log request in development
    logRequest(config)

    return config
  },
  (error) => {
    logError(error)
    return Promise.reject(error)
  }
)

// ============================================================================
// Response Interceptor
// ============================================================================

// Flag to prevent multiple simultaneous token refresh attempts
let isRefreshing = false
let failedQueue = []

/**
 * Process queued requests after token refresh
 *
 * @param {Error|null} error - Error if refresh failed, null if successful
 * @param {string|null} token - New access token if refresh successful
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })

  failedQueue = []
}

/**
 * Handle token refresh and request retry
 */
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response
    logResponse(response)
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Log error
    logError(error)

    // ========================================================================
    // Handle 401 Unauthorized (Token Expired)
    // ========================================================================

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Another request is already refreshing the token
        // Queue this request to be retried after refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return apiClient(originalRequest)
          })
          .catch(err => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')

        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        // Attempt to refresh token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data

        // Store new access token
        localStorage.setItem('access_token', access)

        // Update authorization header
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`
        originalRequest.headers.Authorization = `Bearer ${access}`

        // Process queued requests with new token
        processQueue(null, access)

        isRefreshing = false

        // Retry original request with new token
        return apiClient(originalRequest)

      } catch (refreshError) {
        // Token refresh failed - logout user
        processQueue(refreshError, null)
        isRefreshing = false

        // Clear stored tokens
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')

        // Redirect to login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }

        return Promise.reject(refreshError)
      }
    }

    // ========================================================================
    // Handle Retryable Errors (Network errors, 5xx server errors)
    // ========================================================================

    if (isRetryableError(error) && originalRequest.retryCount < MAX_RETRIES) {
      originalRequest.retryCount++

      const delay = getRetryDelay(originalRequest.retryCount)

      if (isDevelopment) {
        console.log(
          `%c[API Retry] Attempt ${originalRequest.retryCount}/${MAX_RETRIES} after ${delay}ms`,
          'color: #f59e0b; font-weight: bold'
        )
      }

      // Wait before retrying
      await sleep(delay)

      // Retry the request
      return apiClient(originalRequest)
    }

    // ========================================================================
    // Non-retryable error or max retries exceeded
    // ========================================================================

    return Promise.reject(error)
  }
)

// ============================================================================
// API Endpoints
// ============================================================================

/**
 * Authentication API endpoints
 */
export const authAPI = {
  /**
   * Register a new user account
   *
   * @param {object} userData - User registration data
   * @param {string} userData.username - Username
   * @param {string} userData.email - Email address
   * @param {string} userData.password - Password
   * @param {string} userData.password2 - Password confirmation
   * @param {string} userData.first_name - First name
   * @param {string} userData.last_name - Last name
   * @returns {Promise} Axios promise with user data and tokens
   */
  register(userData) {
    return apiClient.post('/auth/register/', userData)
  },

  /**
   * Login with username and password
   *
   * @param {object} credentials - Login credentials
   * @param {string} credentials.username - Username
   * @param {string} credentials.password - Password
   * @returns {Promise} Axios promise with user data and JWT tokens
   */
  login(credentials) {
    return apiClient.post('/auth/login/', credentials)
  },

  /**
   * Logout and blacklist refresh token
   *
   * @param {string} refreshToken - JWT refresh token to blacklist
   * @returns {Promise} Axios promise with logout confirmation
   */
  logout(refreshToken) {
    return apiClient.post('/auth/logout/', { refresh: refreshToken })
  },

  /**
   * Get current user profile
   *
   * @returns {Promise} Axios promise with user profile data
   */
  getProfile() {
    return apiClient.get('/auth/profile/')
  },

  /**
   * Update current user profile
   *
   * @param {object} data - Profile update data
   * @param {string} [data.email] - New email address
   * @param {string} [data.first_name] - New first name
   * @param {string} [data.last_name] - New last name
   * @returns {Promise} Axios promise with updated profile data
   */
  updateProfile(data) {
    return apiClient.patch('/auth/profile/', data)
  },
}

/**
 * Learning content API endpoints
 */
export const learningAPI = {
  /**
   * Get all learning paths (areas with nested content)
   *
   * @returns {Promise} Axios promise with learning areas array
   */
  getLearningPaths() {
    return apiClient.get('/learning-paths/')
  },

  /**
   * Get specific learning path by ID
   *
   * @param {number} id - Learning area ID
   * @returns {Promise} Axios promise with learning area data
   */
  getLearningPath(id) {
    return apiClient.get(`/learning-paths/${id}/`)
  },
}

/**
 * User progress API endpoints
 */
export const progressAPI = {
  /**
   * Get all progress records for current user
   *
   * @returns {Promise} Axios promise with progress records array
   */
  getMyProgress() {
    return apiClient.get('/my-progress/')
  },

  /**
   * Get progress summary statistics for current user
   *
   * @returns {Promise} Axios promise with progress summary data
   */
  getProgressSummary() {
    return apiClient.get('/progress/summary/')
  },

  /**
   * Mark a step as completed
   *
   * @param {number} stepId - Step ID to complete
   * @returns {Promise} Axios promise with updated progress data
   */
  completeStep(stepId) {
    return apiClient.post(`/steps/${stepId}/complete/`)
  },

  /**
   * Create a new progress record
   *
   * @param {object} data - Progress data
   * @param {number} data.step - Step ID
   * @param {string} [data.status] - Progress status
   * @returns {Promise} Axios promise with created progress data
   */
  createProgress(data) {
    return apiClient.post('/progress/', data)
  },

  /**
   * Update an existing progress record
   *
   * @param {number} progressId - Progress record ID
   * @param {object} data - Updated progress data
   * @returns {Promise} Axios promise with updated progress data
   */
  updateProgress(progressId, data) {
    return apiClient.patch(`/progress/${progressId}/`, data)
  },
}

/**
 * Gamification API endpoints
 */
export const gamificationAPI = {
  /**
   * Get current user's gamification profile
   *
   * @returns {Promise} Axios promise with profile data (XP, level, progress)
   */
  getProfile() {
    return apiClient.get('/profile/gamification/')
  },

  /**
   * Get all achievements earned by current user
   *
   * @returns {Promise} Axios promise with user achievements and statistics
   */
  getMyAchievements() {
    return apiClient.get('/my-achievements/')
  },

  /**
   * Get list of all available achievements in the system
   *
   * @returns {Promise} Axios promise with all achievements array
   */
  getAvailableAchievements() {
    return apiClient.get('/achievements/')
  },
}

/**
 * AI Content Generation API endpoints
 */
export const aiAPI = {
  /**
   * Get list of available AI providers
   *
   * @returns {Promise} Axios promise with active AI providers array
   */
  getProviders() {
    return apiClient.get('/ai/providers/')
  },

  /**
   * Get list of content templates
   *
   * @param {string} [contentType] - Filter by content type (optional)
   * @returns {Promise} Axios promise with templates array
   */
  getTemplates(contentType = null) {
    const params = contentType ? { content_type: contentType } : {}
    return apiClient.get('/ai/templates/', { params })
  },

  /**
   * Generate a lesson step using AI
   *
   * @param {object} data - Generation parameters
   * @param {number} data.provider_id - AI provider ID
   * @param {number} [data.template_id] - Content template ID (optional, uses default)
   * @param {string} data.topic - Topic for the lesson
   * @param {string} [data.difficulty] - Difficulty level (beginner/intermediate/advanced)
   * @param {string} [data.language] - Language (default: Portuguese)
   * @param {string} [data.additional_context] - Additional context (optional)
   * @returns {Promise} Axios promise with generated content
   */
  generateLesson(data) {
    return apiClient.post('/ai/generate/lesson/', data)
  },

  /**
   * Generate quiz questions using AI
   *
   * @param {object} data - Generation parameters
   * @param {number} data.provider_id - AI provider ID
   * @param {number} [data.template_id] - Content template ID (optional)
   * @param {string} data.topic - Topic for the quiz
   * @param {number} [data.num_questions] - Number of questions (default: 5)
   * @param {string} [data.difficulty] - Difficulty level
   * @param {string} [data.language] - Language (default: Portuguese)
   * @returns {Promise} Axios promise with generated quiz questions
   */
  generateQuiz(data) {
    return apiClient.post('/ai/generate/quiz/', data)
  },

  /**
   * Get content generation history for current user
   *
   * @param {number} [limit] - Number of records to return (default: 20)
   * @returns {Promise} Axios promise with generation history array
   */
  getHistory(limit = 20) {
    return apiClient.get('/ai/history/', { params: { limit } })
  },

  /**
   * Get detailed information about a specific generation
   *
   * @param {number} generationId - Generation record ID
   * @returns {Promise} Axios promise with full generation details
   */
  getGenerationDetail(generationId) {
    return apiClient.get(`/ai/history/${generationId}/`)
  },

  /**
   * Generate AI-powered hint for code challenge
   *
   * @param {object} data - Hint generation parameters
   * @param {number} data.step_id - Code challenge step ID
   * @param {string} data.user_code - User's current code attempt
   * @param {number} data.attempt_number - Current attempt number
   * @param {string} [data.error_message] - Error message if code failed (optional)
   * @returns {Promise} Axios promise with generated hint
   */
  generateHint(data) {
    return apiClient.post('/ai/generate/hint/', data)
  },
}

// ============================================================================
// Export Default
// ============================================================================

export default apiClient
