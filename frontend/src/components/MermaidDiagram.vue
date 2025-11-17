<template>
  <div class="mermaid-diagram-container">
    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-700 dark:text-red-300 text-sm">
        <strong>Diagram Error:</strong> {{ error }}
      </p>
    </div>
    <div
      v-else
      ref="mermaidContainer"
      class="mermaid-diagram bg-white dark:bg-dark-card p-6 rounded-lg border border-gray-200 dark:border-dark overflow-x-auto"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

// Props
const props = defineProps({
  diagram: {
    type: String,
    required: true
  },
  theme: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'neutral', 'dark', 'forest', 'base'].includes(value)
  }
})

// State
const mermaidContainer = ref(null)
const error = ref(null)
let mermaid = null

// Load and initialize Mermaid
const loadMermaid = async () => {
  try {
    // Load Mermaid from CDN
    if (!window.mermaid) {
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js'
      script.type = 'module'

      await new Promise((resolve, reject) => {
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    mermaid = window.mermaid

    // Initialize Mermaid with configuration
    mermaid.initialize({
      startOnLoad: false,
      theme: props.theme,
      securityLevel: 'loose',
      fontFamily: 'inherit',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true
      }
    })

    await renderDiagram()
  } catch (err) {
    console.error('Failed to load Mermaid:', err)
    error.value = 'Failed to load diagram renderer'
  }
}

// Render diagram
const renderDiagram = async () => {
  if (!mermaidContainer.value || !mermaid) return

  error.value = null

  try {
    // Clear previous content
    mermaidContainer.value.innerHTML = ''

    // Generate unique ID for diagram
    const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

    // Render diagram
    const { svg } = await mermaid.render(id, props.diagram)

    // Insert SVG
    mermaidContainer.value.innerHTML = svg
  } catch (err) {
    console.error('Mermaid render error:', err)
    error.value = err.message || 'Invalid diagram syntax'
  }
}

// Watch for diagram changes
watch(() => props.diagram, async () => {
  if (mermaid) {
    await renderDiagram()
  }
})

// Lifecycle
onMounted(() => {
  loadMermaid()
})
</script>

<style scoped>
.mermaid-diagram {
  min-height: 100px;
}

/* Ensure diagrams are visible in dark mode */
.dark .mermaid-diagram :deep(svg) {
  filter: invert(0.9) hue-rotate(180deg);
}

/* Better text rendering */
.mermaid-diagram :deep(text) {
  font-family: inherit !important;
}

/* Responsive diagrams */
.mermaid-diagram :deep(svg) {
  max-width: 100%;
  height: auto;
}
</style>
