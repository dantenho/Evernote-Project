<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-green-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="text-center">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          🎓 Master New Skills with LearnHub
        </h1>
        <p class="text-xl text-gray-700 mb-12 max-w-2xl mx-auto">
          Your personalized learning journey starts here. Track your progress,
          complete lessons, and test your knowledge with interactive quizzes.
        </p>

        <div class="flex justify-center space-x-4">
          <router-link to="/register" class="btn btn-primary text-lg px-8 py-3">
            Get Started
          </router-link>
          <router-link to="/login" class="btn btn-secondary text-lg px-8 py-3">
            Sign In
          </router-link>
        </div>
      </div>

      <div class="mt-20 grid md:grid-cols-3 gap-8">
        <div class="card text-center">
          <div class="text-4xl mb-4">📚</div>
          <h3 class="text-xl font-semibold mb-2">Structured Learning</h3>
          <p class="text-gray-600">
            Follow carefully designed learning paths to master any subject.
          </p>
        </div>

        <div class="card text-center">
          <div class="text-4xl mb-4">📊</div>
          <h3 class="text-xl font-semibold mb-2">Track Progress</h3>
          <p class="text-gray-600">
            Monitor your learning journey and celebrate your achievements.
          </p>
        </div>

        <div class="card text-center">
          <div class="text-4xl mb-4">🎯</div>
          <h3 class="text-xl font-semibold mb-2">Interactive Quizzes</h3>
          <p class="text-gray-600">
            Test your knowledge with engaging quizzes and get instant feedback.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Home view - landing page
</script>
