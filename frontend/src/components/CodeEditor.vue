<template>
  <div class="code-editor-container">
    <!-- Instructions -->
    <div v-if="instructions" class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div v-html="instructions" class="prose prose-sm max-w-none"></div>
    </div>

    <!-- Editor -->
    <div class="editor-wrapper rounded-lg overflow-hidden shadow-lg border-2" :class="editorBorderClass">
      <!-- Toolbar -->
      <div class="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-gray-300 text-sm font-mono">🐍 Python</span>
          <span v-if="isRunning" class="text-yellow-400 text-xs animate-pulse">● Running...</span>
          <span v-else-if="hasOutput" class="text-green-400 text-xs">● Ready</span>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="resetCode"
            class="text-gray-400 hover:text-white text-xs px-2 py-1 rounded transition-colors"
            title="Reset Code"
          >
            ↺ Reset
          </button>
          <button
            v-if="showSolution"
            @click="viewSolution"
            class="text-yellow-400 hover:text-yellow-300 text-xs px-2 py-1 rounded transition-colors"
            title="View Solution"
          >
            💡 Solution
          </button>
        </div>
      </div>

      <!-- Code Textarea -->
      <textarea
        ref="codeInput"
        v-model="userCode"
        @keydown.tab.prevent="handleTab"
        class="w-full bg-gray-900 text-gray-100 font-mono text-sm p-4 focus:outline-none resize-none"
        :rows="codeLines"
        spellcheck="false"
        :disabled="isRunning"
      ></textarea>

      <!-- Run Button -->
      <div class="bg-gray-800 px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <button
            @click="runCode"
            :disabled="isRunning || !pyodideReady"
            class="btn px-6 py-2 rounded-lg font-semibold transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isRunning ? 'bg-yellow-500 text-white' : 'bg-green-500 hover:bg-green-600 text-white'"
          >
            <span v-if="isRunning">⚙️ Running...</span>
            <span v-else-if="!pyodideReady">⏳ Loading Python...</span>
            <span v-else>▶️ Run Code</span>
          </button>
          <span v-if="executionTime" class="text-gray-400 text-xs">
            ⏱️ {{ executionTime }}ms
          </span>
        </div>
        <div v-if="isCorrect !== null" class="flex items-center space-x-2">
          <span v-if="isCorrect" class="text-green-400 text-sm font-semibold flex items-center space-x-1">
            <span>✓</span>
            <span>Correct!</span>
          </span>
          <span v-else class="text-red-400 text-sm font-semibold flex items-center space-x-1">
            <span>✗</span>
            <span>Try Again</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Output -->
    <div v-if="hasOutput" class="mt-4 rounded-lg overflow-hidden border-2" :class="outputBorderClass">
      <!-- Output Header -->
      <div class="px-4 py-2 flex items-center justify-between" :class="outputHeaderClass">
        <span class="text-sm font-semibold">Output:</span>
        <button
          @click="clearOutput"
          class="text-xs px-2 py-1 rounded hover:bg-white hover:bg-opacity-10 transition-colors"
        >
          Clear
        </button>
      </div>

      <!-- Output Content -->
      <div class="bg-gray-900 text-gray-100 font-mono text-sm p-4 max-h-64 overflow-y-auto">
        <pre class="whitespace-pre-wrap">{{ output }}</pre>
        <div v-if="errorOutput" class="text-red-400 mt-2">
          <strong>Error:</strong>
          <pre class="whitespace-pre-wrap">{{ errorOutput }}</pre>
        </div>
      </div>

      <!-- Expected vs Actual (if checking) -->
      <div v-if="expectedOutput && output !== expectedOutput" class="bg-yellow-50 border-t border-yellow-200 p-3">
        <p class="text-xs font-semibold text-yellow-800 mb-1">Expected Output:</p>
        <pre class="text-xs text-yellow-700 whitespace-pre-wrap font-mono">{{ expectedOutput }}</pre>
      </div>
    </div>

    <!-- Hints -->
    <div v-if="hints && hints.length > 0" class="mt-4">
      <button
        @click="showHints = !showHints"
        class="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
      >
        <span>{{ showHints ? '▼' : '▶' }}</span>
        <span>💡 Need help? View hints ({{ hints.length }})</span>
      </button>
      <div v-if="showHints" class="mt-2 space-y-2">
        <div
          v-for="(hint, index) in hints"
          :key="index"
          class="p-3 bg-purple-50 border border-purple-200 rounded-lg text-sm"
        >
          <strong class="text-purple-800">Hint {{ index + 1 }}:</strong>
          <p class="text-purple-700 mt-1">{{ hint }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

// ============================================================================
// Props
// ============================================================================

const props = defineProps({
  initialCode: {
    type: String,
    default: '# Write your code here\nprint("Hello, World!")'
  },
  expectedOutput: {
    type: String,
    default: null
  },
  instructions: {
    type: String,
    default: null
  },
  solution: {
    type: String,
    default: null
  },
  hints: {
    type: Array,
    default: () => []
  },
  showSolution: {
    type: Boolean,
    default: false
  }
})

// ============================================================================
// Emits
// ============================================================================

const emit = defineEmits(['correct', 'run', 'error'])

// ============================================================================
// State
// ============================================================================

const userCode = ref(props.initialCode || '')
const output = ref('')
const errorOutput = ref('')
const isRunning = ref(false)
const pyodideReady = ref(false)
const pyodide = ref(null)
const executionTime = ref(null)
const isCorrect = ref(null)
const showHints = ref(false)

// ============================================================================
// Computed
// ============================================================================

const hasOutput = computed(() => output.value || errorOutput.value)

const codeLines = computed(() => {
  const lines = userCode.value.split('\n').length
  return Math.max(10, Math.min(lines + 2, 25))
})

const outputBorderClass = computed(() => {
  if (isCorrect.value === true) return 'border-green-400'
  if (isCorrect.value === false) return 'border-red-400'
  return 'border-gray-300'
})

const outputHeaderClass = computed(() => {
  if (isCorrect.value === true) return 'bg-green-500 text-white'
  if (isCorrect.value === false) return 'bg-red-500 text-white'
  return 'bg-gray-700 text-gray-100'
})

const editorBorderClass = computed(() => {
  if (isCorrect.value === true) return 'border-green-400'
  if (isCorrect.value === false) return 'border-red-400'
  return 'border-gray-300'
})

// ============================================================================
// Methods
// ============================================================================

/**
 * Load Pyodide (Python in browser)
 */
const loadPyodide = async () => {
  try {
    console.log('Loading Pyodide...')

    // Load Pyodide from CDN
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js'
    script.async = true

    script.onload = async () => {
      // Wait for loadPyodide to be available
      if (typeof loadPyodide === 'undefined') {
        console.error('loadPyodide not found')
        return
      }

      pyodide.value = await window.loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/'
      })

      pyodideReady.value = true
      console.log('Pyodide ready!')
    }

    script.onerror = () => {
      console.error('Failed to load Pyodide')
      errorOutput.value = 'Failed to load Python environment. Please refresh the page.'
    }

    document.head.appendChild(script)

  } catch (err) {
    console.error('Pyodide load error:', err)
    errorOutput.value = 'Failed to initialize Python environment'
  }
}

/**
 * Run Python code
 */
const runCode = async () => {
  if (!pyodideReady.value || isRunning.value) return

  isRunning.value = true
  output.value = ''
  errorOutput.value = ''
  isCorrect.value = null
  executionTime.value = null

  const startTime = performance.now()

  try {
    // Redirect Python stdout to capture print output
    await pyodide.value.runPython(`
import sys
import io
sys.stdout = io.StringIO()
    `)

    // Run user code
    await pyodide.value.runPython(userCode.value)

    // Get output
    const stdout = await pyodide.value.runPython('sys.stdout.getvalue()')
    output.value = stdout

    // Calculate execution time
    executionTime.value = Math.round(performance.now() - startTime)

    // Check if correct (if expected output provided)
    if (props.expectedOutput) {
      const actualOutput = output.value.trim()
      const expectedOutput = props.expectedOutput.trim()

      if (actualOutput === expectedOutput) {
        isCorrect.value = true
        emit('correct', { output: actualOutput, time: executionTime.value })
      } else {
        isCorrect.value = false
      }
    }

    emit('run', { output: output.value, time: executionTime.value })

  } catch (err) {
    console.error('Python execution error:', err)
    errorOutput.value = err.message || String(err)
    isCorrect.value = false
    emit('error', err)

  } finally {
    isRunning.value = false
  }
}

/**
 * Reset code to initial state
 */
const resetCode = () => {
  userCode.value = props.initialCode || ''
  output.value = ''
  errorOutput.value = ''
  isCorrect.value = null
  executionTime.value = null
}

/**
 * View solution
 */
const viewSolution = () => {
  if (props.solution) {
    userCode.value = props.solution
  }
}

/**
 * Clear output
 */
const clearOutput = () => {
  output.value = ''
  errorOutput.value = ''
  isCorrect.value = null
}

/**
 * Handle Tab key in textarea
 */
const handleTab = (event) => {
  const textarea = event.target
  const start = textarea.selectionStart
  const end = textarea.selectionEnd

  // Insert 4 spaces
  userCode.value = userCode.value.substring(0, start) + '    ' + userCode.value.substring(end)

  // Move cursor after spaces
  textarea.selectionStart = textarea.selectionEnd = start + 4
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadPyodide()
})

// Watch for prop changes
watch(() => props.initialCode, (newCode) => {
  if (newCode) {
    userCode.value = newCode
  }
})
</script>

<style scoped>
.code-editor-container {
  width: 100%;
}

textarea {
  line-height: 1.5;
  tab-size: 4;
}

textarea:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

pre {
  margin: 0;
  font-family: 'Courier New', monospace;
}

/* Scrollbar styling */
.max-h-64::-webkit-scrollbar {
  width: 8px;
}

.max-h-64::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.max-h-64::-webkit-scrollbar-thumb {
  background: #4a4a4a;
  border-radius: 4px;
}

.max-h-64::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
