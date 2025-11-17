<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 animate-fade-in" @click="$emit('close')">
    <div class="bg-white dark:bg-dark-card rounded-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden animate-scale-in" @click.stop>
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-dark flex items-center justify-between">
        <h3 class="text-xl font-bold text-gray-900 dark:text-dark-primary flex items-center space-x-2">
          <span class="text-2xl">📊</span>
          <span>Mermaid Diagram Editor</span>
        </h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700 dark:text-dark-muted dark:hover:text-dark-primary">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
        <!-- Templates -->
        <div class="mb-6">
          <h4 class="text-sm font-semibold text-gray-700 dark:text-dark-secondary mb-3">Quick Templates</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <button
              v-for="(template, key) in templates"
              :key="key"
              @click="loadTemplate(key)"
              class="p-3 border-2 border-gray-200 dark:border-dark rounded-lg hover:border-primary-500 dark:hover:border-primary-400 transition-all text-left"
            >
              <div class="text-lg mb-1">{{ template.icon }}</div>
              <div class="text-xs font-medium text-gray-900 dark:text-dark-primary">{{ template.name }}</div>
            </button>
          </div>
        </div>

        <!-- Editor Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Code Editor -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <label class="text-sm font-semibold text-gray-700 dark:text-dark-secondary">Diagram Code</label>
              <button
                @click="copyCode"
                class="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center space-x-1"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Copy</span>
              </button>
            </div>
            <textarea
              v-model="diagramCode"
              class="w-full h-96 p-4 font-mono text-sm bg-gray-50 dark:bg-dark border border-gray-300 dark:border-dark rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
              placeholder="Enter your Mermaid diagram code here..."
              spellcheck="false"
            ></textarea>
          </div>

          <!-- Preview -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-dark-secondary mb-3">Live Preview</label>
            <div class="border-2 border-gray-200 dark:border-dark rounded-lg h-96 overflow-auto">
              <MermaidDiagram
                v-if="diagramCode.trim()"
                :diagram="diagramCode"
                :theme="isDark ? 'dark' : 'default'"
              />
              <div v-else class="flex items-center justify-center h-full text-gray-400 dark:text-dark-muted">
                <div class="text-center">
                  <svg class="w-16 h-16 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0h2a2 2 0 012 2v6a2 2 0 01-2 2h-2a2 2 0 01-2-2v-6z" />
                  </svg>
                  <p>No diagram yet</p>
                  <p class="text-xs mt-1">Enter code or choose a template</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Documentation Link -->
        <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p class="text-sm text-blue-700 dark:text-blue-300">
            <strong>📘 Need help?</strong> Check the
            <a href="https://mermaid.js.org/syntax/flowchart.html" target="_blank" rel="noopener" class="underline hover:text-blue-900 dark:hover:text-blue-100">
              Mermaid documentation
            </a>
            for syntax and examples.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-dark flex justify-end space-x-3">
        <button @click="$emit('close')" class="btn btn-secondary">
          Close
        </button>
        <button @click="saveDiagram" class="btn btn-primary flex items-center space-x-2">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
          </svg>
          <span>Save Diagram</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useTheme } from '@/composables/useTheme'
import MermaidDiagram from './MermaidDiagram.vue'

// Emits
const emit = defineEmits(['close', 'save'])

// Composables
const { isDark } = useTheme()

// State
const diagramCode = ref('')

// Templates
const templates = {
  flowchart: {
    name: 'Flowchart',
    icon: '🔄',
    code: `flowchart TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
    C --> E[End]`
  },
  sequence: {
    name: 'Sequence',
    icon: '📨',
    code: `sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database

    User->>Frontend: Click button
    Frontend->>Backend: API Request
    Backend->>Database: Query data
    Database-->>Backend: Return results
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display data`
  },
  classDiagram: {
    name: 'Class Diagram',
    icon: '📦',
    code: `classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +boolean indoor
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat`
  },
  gitGraph: {
    name: 'Git Graph',
    icon: '🌳',
    code: `gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Add feature"
    checkout main
    merge develop
    commit id: "Release v1.0"`
  },
  pie: {
    name: 'Pie Chart',
    icon: '🥧',
    code: `pie title Programming Languages
    "Python" : 35
    "JavaScript" : 30
    "Java" : 20
    "C++" : 10
    "Others" : 5`
  },
  mindmap: {
    name: 'Mind Map',
    icon: '🧠',
    code: `mindmap
  root((Learning))
    Topics
      Programming
        Python
        JavaScript
      Mathematics
        Algebra
        Calculus
      Science
        Physics
        Chemistry`
  },
  timeline: {
    name: 'Timeline',
    icon: '📅',
    code: `timeline
    title Project Development Timeline
    2024-01 : Planning
            : Requirements gathering
    2024-02 : Development
            : Backend API
            : Frontend UI
    2024-03 : Testing
            : QA & Bug fixes
    2024-04 : Release
            : Deploy to production`
  },
  erDiagram: {
    name: 'ER Diagram',
    icon: '🗄️',
    code: `erDiagram
    USER ||--o{ ORDER : places
    USER {
        string username
        string email
        int id
    }
    ORDER ||--|{ ITEM : contains
    ORDER {
        int order_id
        date order_date
        float total
    }
    ITEM {
        int item_id
        string name
        float price
    }`
  }
}

// Methods
const loadTemplate = (key) => {
  diagramCode.value = templates[key].code
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(diagramCode.value)
    // Could add a toast notification here
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const saveDiagram = () => {
  if (diagramCode.value.trim()) {
    emit('save', diagramCode.value)
    emit('close')
  }
}
</script>
