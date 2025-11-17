# Learning App - Frontend

A modern Vue.js 3 frontend application for a Duolingo-style learning platform with authentication, progress tracking, and interactive lessons/quizzes.

## 🚀 Features

- **Authentication System**: User registration, login, logout, and profile management
- **Learning Dashboard**: Browse and access learning areas, topics, and tracks
- **Interactive Lessons**: Text and video-based learning content
- **Quiz System**: Multiple-choice quizzes with instant feedback and explanations
- **Progress Tracking**: Real-time progress tracking with completion statistics
- **Responsive Design**: Mobile-first design using Tailwind CSS
- **State Management**: Centralized state with Pinia
- **JWT Authentication**: Secure token-based authentication with automatic refresh

## 🛠️ Tech Stack

- **Vue 3** (Composition API)
- **Vite** - Fast build tool and dev server
- **Vue Router 4** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first CSS framework

## 📋 Prerequisites

- Node.js 16+ and npm/yarn
- Backend API running on `http://localhost:8000` (Django)

## 🔧 Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Environment Configuration:**

The application is configured to proxy API requests to `http://localhost:8000` via Vite. If your backend runs on a different port, update `vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT',
      changeOrigin: true,
    },
  },
},
```

3. **Start development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

4. **Build for production:**
```bash
npm run build
```

5. **Preview production build:**
```bash
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── assets/          # CSS, images, fonts
│   │   └── main.css     # Global styles with Tailwind
│   ├── components/      # Reusable Vue components
│   │   └── NavBar.vue   # Navigation component
│   ├── router/          # Vue Router configuration
│   │   └── index.js     # Route definitions and guards
│   ├── services/        # External services
│   │   └── api.js       # Axios client with interceptors
│   ├── stores/          # Pinia stores
│   │   ├── auth.js      # Authentication state
│   │   └── learning.js  # Learning content state
│   ├── views/           # Page components
│   │   ├── HomeView.vue       # Landing page
│   │   ├── LoginView.vue      # Login page
│   │   ├── RegisterView.vue   # Registration page
│   │   ├── DashboardView.vue  # Main dashboard
│   │   ├── LearnView.vue      # Lesson/quiz viewer
│   │   ├── ProgressView.vue   # Progress tracking
│   │   └── ProfileView.vue    # User profile
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── index.html           # HTML entry point
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── postcss.config.js    # PostCSS configuration
```

## 🔑 Key Components

### Authentication Flow

**LoginView** (`src/views/LoginView.vue`)
- Username/password authentication
- JWT token storage in localStorage
- Redirects to dashboard on success

**RegisterView** (`src/views/RegisterView.vue`)
- User registration with validation
- Automatic login after registration
- Duplicate username/email validation

### Learning Interface

**DashboardView** (`src/views/DashboardView.vue`)
- Displays all learning areas, topics, and tracks
- Shows progress summary statistics
- Step-level progress indicators
- Click-to-navigate to lessons/quizzes

**LearnView** (`src/views/LearnView.vue`)
- Dynamic viewer for both lessons and quizzes
- Video embedding for lesson content
- Interactive quiz with multiple-choice questions
- Automatic step completion on quiz pass (70%+)
- Retry functionality for failed quizzes

**ProgressView** (`src/views/ProgressView.vue`)
- Overall progress statistics
- Progress breakdown by learning area
- Recently completed steps
- In-progress steps with quick links

**ProfileView** (`src/views/ProfileView.vue`)
- View and edit profile information
- Account statistics
- Sign out functionality

## 🗂️ State Management

### Auth Store (`src/stores/auth.js`)

Manages user authentication and profile:

```javascript
// State
{
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null
}

// Actions
login(credentials)        // Login with username/password
register(userData)        // Register new user
logout()                  // Logout and clear tokens
fetchProfile()            // Get current user profile
updateProfile(data)       // Update user profile
```

### Learning Store (`src/stores/learning.js`)

Manages learning content and progress:

```javascript
// State
{
  learningPaths: [],      // All areas/topics/tracks/steps
  currentStep: null,      // Currently viewing step
  userProgress: [],       // User's progress records
  progressSummary: null,  // Statistics
  loading: false,
  error: null
}

// Actions
fetchLearningPaths()      // Get all learning content
fetchUserProgress()       // Get user's progress
fetchProgressSummary()    // Get progress statistics
completeStep(stepId)      // Mark step as complete
setCurrentStep(step)      // Set current viewing step

// Getters
allAreas                  // All learning areas
getStepById(stepId)       // Find step by ID
isStepCompleted(stepId)   // Check if step completed
getProgressForStep(stepId) // Get progress for step
```

## 🌐 API Integration

The frontend communicates with the Django REST API via Axios with automatic:

- JWT token injection in request headers
- Token refresh on 401 responses
- Error handling and retry logic

**API Endpoints:**

```
POST   /api/v1/auth/register/          # User registration
POST   /api/v1/auth/login/             # User login (JWT)
POST   /api/v1/auth/refresh/           # Token refresh
POST   /api/v1/auth/logout/            # User logout
GET    /api/v1/auth/profile/           # Get user profile
PATCH  /api/v1/auth/profile/           # Update profile

GET    /api/v1/learning-paths/         # Get all learning paths
GET    /api/v1/my-progress/            # Get user progress
GET    /api/v1/progress/summary/       # Get progress summary
POST   /api/v1/steps/{id}/complete/    # Mark step complete
```

## 🎨 Styling

The application uses **Tailwind CSS** with custom utility classes:

**Custom Classes** (defined in `src/assets/main.css`):

```css
.btn               /* Base button styles */
.btn-primary       /* Primary button (green) */
.btn-secondary     /* Secondary button (gray) */
.card              /* Card container with shadow */
.input             /* Form input styles */
```

**Color Palette:**

- Primary: Green (`primary-*` classes)
- Success: Green
- Info: Blue
- Error: Red
- Gray scale for text and backgrounds

## 🔐 Authentication Guards

Routes are protected using Vue Router navigation guards:

```javascript
// Protected route example
{
  path: '/dashboard',
  name: 'Dashboard',
  component: DashboardView,
  meta: { requiresAuth: true }  // Requires authentication
}
```

Unauthenticated users are redirected to `/login` when accessing protected routes.

## 🧪 Development

### Running the Application

1. Ensure the Django backend is running on `http://localhost:8000`
2. Start the frontend dev server: `npm run dev`
3. Access the application at `http://localhost:5173`

### Creating Test Users

Use the registration page or create users via Django admin:

```bash
cd ..  # Go to project root
python manage.py createsuperuser
```

### Hot Module Replacement

Vite provides instant HMR for a smooth development experience. Changes to Vue components, styles, and JavaScript will reflect immediately without full page reloads.

## 🚢 Deployment

### Production Build

```bash
npm run build
```

This creates optimized static files in the `dist/` directory.

### Serving Production Build

You can serve the production build using:

```bash
npm run preview
```

Or deploy the `dist/` directory to any static hosting service (Netlify, Vercel, AWS S3, etc.).

### Environment Variables

For production, you may want to use environment variables for the API URL:

1. Create `.env.production`:
```
VITE_API_BASE_URL=https://your-api-domain.com
```

2. Update `src/services/api.js` to use the env variable:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

## 📝 Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint (if configured)
```

## 🐛 Troubleshooting

**Issue: API requests fail with CORS errors**
- Ensure Django CORS settings include `http://localhost:5173`
- Check that `django-cors-headers` is installed and configured

**Issue: Token refresh not working**
- Verify JWT settings in Django (`SIMPLE_JWT`)
- Check that refresh token is stored in localStorage
- Ensure `/api/v1/auth/refresh/` endpoint is accessible

**Issue: Routes not working after page refresh**
- This is expected in development mode with client-side routing
- For production, configure your web server to redirect all routes to `index.html`

**Issue: Tailwind styles not applying**
- Run `npm install` to ensure PostCSS and Tailwind are installed
- Check that `tailwind.config.js` includes correct content paths
- Verify `main.css` imports Tailwind directives

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is part of a learning application and is for educational purposes.

## 🔗 Related Documentation

- [Backend API Documentation](../API_DOCUMENTATION.md)
- [Testing Documentation](../TESTING.md)
- [Vue.js Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
