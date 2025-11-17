# 🧪 Testing Guide - LearnHub Platform

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Testing as Admin](#testing-as-admin)
3. [Testing as Student](#testing-as-student)
4. [Testing AI Features](#testing-ai-features)
5. [Docker Testing](#docker-testing)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Backend dependencies
pip install -r requirements.txt

# Optional: AI features
pip install -r requirements-ai.txt

# Database
# Make sure PostgreSQL is running
```

### Initial Setup
```bash
# 1. Run migrations
python manage.py migrate

# 2. Create superuser (admin)
python manage.py createsuperuser

# 3. Initialize AI templates (optional)
python manage.py init_ai_templates

# 4. Seed Python track
python manage.py seed_python_track

# 5. Start backend
python manage.py runserver

# 6. In another terminal, start frontend
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1
- **Django Admin**: http://localhost:8000/admin

---

## 👨‍💼 Testing as Admin

### 1. Access Django Admin
```
URL: http://localhost:8000/admin
Login: Use superuser credentials
```

### 2. View Created Python Track
1. Go to **Areas** section
2. You should see:
   - **Area**: "Programming" 💻
   - **Topic**: "Python Basics" 🐍
   - **Track**: "Introduction to Python" 🚀
   - **Steps**: 10 exercises (5 lessons + 5 quizzes)

### 3. View Gamification Settings
1. **Achievements**:
   - Navigate to "Achievements" in admin
   - Check rank milestones, XP milestones, streak milestones
   - View course completion badges

2. **User Profiles**:
   - Navigate to "User profiles"
   - See XP points, rank, streaks for each user
   - Check rank progress and achievements earned

### 4. Configure AI Providers (Optional)
1. Navigate to "AI Providers"
2. Click "Add AI Provider"
3. Example setups:

#### Ollama (Local - No API Key Needed)
```
Name: Ollama Llama 2
Provider Type: Ollama (Local)
API Endpoint: http://localhost:11434
Model Name: llama2
Max Tokens: 2000
Temperature: 0.7
```

#### Claude (Anthropic)
```
Name: Claude Sonnet
Provider Type: Claude (Anthropic)
API Key: sk-ant-api03-xxxxx
Model Name: claude-sonnet-4-5-20250929
Max Tokens: 2000
Temperature: 0.7
```

#### Transformers (Local)
```
Name: Local GPT-2
Provider Type: Transformers (Hugging Face Local)
Model Name: gpt2
Max Tokens: 500
Temperature: 0.8
```

### 5. Create Content Templates (Optional)
1. Navigate to "Content templates"
2. Run: `python manage.py init_ai_templates`
3. Or create manually with system/user prompts

---

## 🎓 Testing as Student

### 1. Register New Account
```
URL: http://localhost:5173/register
Fill in:
- Username
- Email
- Password
- First Name
- Last Name
```

### 2. View Dashboard
After login, you'll see:
- **Progress Summary**: Total steps, completed, in progress, completion %
- **Programming Area**: With Python Basics topic
- **Python Track Card**:
  - Title: "Introduction to Python"
  - Progress bar (0% initially)
  - "🚀 Start Track" button
  - 10 exercises count
  - Difficulty: beginner

### 3. Start Learning Journey

#### Click "Start Track" Button
- Automatically navigates to first exercise
- Shows progress bar at top (1/10)
- Displays XP reward (10 XP)

#### Lesson Experience (Exercise 1: "What is Python?")
✅ **What You'll See**:
- Beautiful formatted content with headings
- Code snippet with copy button:
  ```python
  print("Hello, World!")
  ```
- "Continue" button at bottom

✅ **What to Test**:
1. Read the lesson content
2. Try copying the code snippet (click 📋 Copy Code)
3. Click "Continue" button
4. **Celebration Modal** appears:
   - 🎉 Awesome!
   - "You've earned 10 XP"
   - XP display animation
   - "Continue →" button
5. Click "Continue" - goes to next exercise

#### Quiz Experience (Exercise 2: "Python Basics Quiz")
✅ **What You'll See**:
- Question counter: "Question 1 of X"
- Question text
- 4 multiple choice options (A, B, C, D)

✅ **What to Test**:
1. Read question: "What does the print() function do in Python?"
2. Click an answer (try wrong answer first)
3. **Immediate Feedback**:
   - Wrong answer turns RED ✗
   - Correct answer shows GREEN ✓
   - Explanation appears below
   - Example: "print() is for displaying output, not calculations"
4. Click "Next Question" button
5. Progress dots at bottom show which questions done
6. Complete all questions
7. Click "Complete Quiz"
8. Celebration modal with XP reward
9. Continue to next exercise

### 4. Test Complete Flow (All 10 Exercises)

#### Expected Sequence:
1. ✅ Lesson: What is Python? (10 XP)
2. ✅ Quiz: Python Basics Quiz (10 XP)
3. ✅ Lesson: Storing Data in Variables (10 XP)
4. ✅ Quiz: Variables Quiz (10 XP)
5. ✅ Lesson: Working with Numbers (10 XP)
6. ✅ Quiz: Math Operations Quiz (10 XP)
7. ✅ Lesson: Text with Strings (10 XP)
8. ✅ Quiz: Strings Quiz (10 XP)
9. ✅ Lesson: Organizing Data with Lists (10 XP)
10. ✅ Quiz: Python Fundamentals - Final Quiz (20 XP)

**Total XP**: 110 XP

### 5. Check Progress After Completion

#### In NavBar (Top Right)
✅ **Desktop View**:
- Rank badge with icon and color
- XP points display
- Progress bar to next rank
- Streak count (if applicable)

✅ **Mobile View**:
- Compact: Icon + Rank + Streak

#### In Dashboard
- Track shows 100% complete (green badge)
- Progress bar fully filled
- Button says "▶️ Continue Learning" (can restart)
- All 10 exercises have ✓ checkmarks

#### In Profile Page
Visit `/profile`:
- **Rank Banner**:
  - Large rank icon with animation
  - Current rank name and color
  - Total XP: 110
  - Rank progress bar
- **Streak Display**:
  - 🔥 Current streak
  - Best streak record
- **Quick Stats Grid**:
  - Days active
  - Total XP
  - Rank tier
  - Achievements count

---

## 🤖 Testing AI Features

### 1. Access AI Generator
```
URL: http://localhost:5173/ai-generator
Or: Click "🤖 AI Generator" in navbar
```

### 2. Generate Lesson Content

#### Step-by-Step:
1. **Select Content Type**: Click "📚 Lesson"
2. **Select AI Provider**: Choose from dropdown
   - Ollama (if running locally)
   - Or any configured provider
3. **Enter Topic**: e.g., "Python Functions"
4. **Select Difficulty**: Intermediate
5. **Select Language**: Portuguese (or English)
6. **Additional Context** (optional): "Focus on practical examples"
7. **Click "Generate Content"**

#### What to Expect:
- Loading state with spinner
- Generation time: ~5-30 seconds depending on provider
- Results display:
  - Generated text (formatted)
  - Tokens used
  - Generation time
  - "Copy to Clipboard" button

### 3. Generate Quiz Questions

#### Step-by-Step:
1. **Select Content Type**: Click "❓ Quiz"
2. **Select AI Provider**: Same as above
3. **Enter Topic**: e.g., "Python Loops"
4. **Number of Questions**: 5
5. **Select Difficulty**: Beginner
6. **Select Language**: Portuguese
7. **Click "Generate Content"**

#### What to Expect:
- JSON formatted quiz questions
- Each question with 4 alternatives
- Correct answers marked
- Explanations included

### 4. View Generation History
- Right sidebar shows recent 10 generations
- Click on any item to view details
- Shows success/failure status
- Provider used and timestamp

---

## 🐳 Docker Testing

### Using Docker Compose

#### 1. Build and Start Services
```bash
# Start all services
docker-compose -f docker-compose.ai.yml up -d

# View logs
docker-compose -f docker-compose.ai.yml logs -f

# Check status
docker-compose -f docker-compose.ai.yml ps
```

#### 2. Services Running
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Ollama**: localhost:11434
- **Django**: localhost:8000
- **Frontend**: localhost:5173
- **Nginx**: localhost:80

#### 3. Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.ai.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.ai.yml exec web python manage.py createsuperuser

# Seed Python track
docker-compose -f docker-compose.ai.yml exec web python manage.py seed_python_track

# Initialize AI templates
docker-compose -f docker-compose.ai.yml exec web python manage.py init_ai_templates
```

#### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Admin: http://localhost:8000/admin

#### 5. Test Ollama Integration
```bash
# Pull a model
docker-compose -f docker-compose.ai.yml exec ollama ollama pull llama2

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "What is Python?",
  "stream": false
}'
```

#### 6. Stop Services
```bash
docker-compose -f docker-compose.ai.yml down

# With volume cleanup
docker-compose -f docker-compose.ai.yml down -v
```

---

## ✅ Testing Checklist

### Backend Tests
- [ ] Migrations run successfully
- [ ] Admin panel accessible
- [ ] Python track created with 10 exercises
- [ ] User registration works
- [ ] Authentication (login/logout) works
- [ ] API endpoints respond correctly
- [ ] AI providers can be configured
- [ ] Content generation works (if AI configured)

### Frontend Tests
- [ ] Dashboard loads and displays tracks
- [ ] Track cards show progress
- [ ] "Start Track" button navigates correctly
- [ ] Lesson view displays content properly
- [ ] Code snippets can be copied
- [ ] Quiz view shows questions
- [ ] Answer selection provides feedback
- [ ] Question navigation works
- [ ] Celebration modal appears on completion
- [ ] XP is awarded and displayed
- [ ] Progress bars update correctly
- [ ] Navbar shows rank and XP
- [ ] Profile page displays gamification data
- [ ] Mobile responsiveness works
- [ ] Animations are smooth

### Gamification Tests
- [ ] XP awarded after completing exercises
- [ ] Rank updates based on XP
- [ ] Streak tracks consecutive days
- [ ] Achievements are earned
- [ ] Progress persists across sessions
- [ ] Completion status saved correctly

### AI Features Tests (Optional)
- [ ] AI providers can be added in admin
- [ ] Templates can be created/modified
- [ ] Content generation succeeds
- [ ] Generated content is well-formatted
- [ ] Generation history is saved
- [ ] Different providers work correctly
- [ ] Error handling works gracefully

### Docker Tests
- [ ] All services start successfully
- [ ] Database persists data
- [ ] Ollama model downloads work
- [ ] Application accessible through Nginx
- [ ] Redis caching functional
- [ ] Health checks pass
- [ ] Services restart on failure

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Check connection settings in .env
DB_HOST=localhost
DB_PORT=5432
```

### Frontend Not Loading
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/auth/profile/

# Check frontend dev server
cd frontend
npm run dev
```

### AI Generation Fails
```bash
# Check provider is active
# Check API key is correct
# Check endpoint is reachable
# Check logs for specific error
python manage.py shell
>>> from learning.models import AIProvider
>>> AIProvider.objects.filter(is_active=True)
```

### Ollama Not Working
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull a model first
ollama pull llama2

# Test in Python
python manage.py shell
>>> from learning.ai_services import OllamaService
>>> from learning.models import AIProvider
>>> provider = AIProvider.objects.get(provider_type='ollama')
>>> service = OllamaService(provider)
>>> result = service.generate("You are a teacher", "What is Python?")
```

---

## 📊 Expected Results Summary

After completing all tests, you should have:

### Student Account
- ✅ 110 XP earned
- ✅ Rank: Bronze I or higher
- ✅ 10/10 exercises completed
- ✅ Python Basics track 100% complete
- ✅ Streak of 1 day (or more if tested on multiple days)

### Admin Panel
- ✅ 1 Area (Programming)
- ✅ 1 Topic (Python Basics)
- ✅ 1 Track (Introduction to Python)
- ✅ 10 Steps (5 lessons + 5 quizzes)
- ✅ AI Providers configured (if tested)
- ✅ Content Templates initialized

### Application Features
- ✅ Full Mimo/Duolingo-style navigation
- ✅ Gamification system working
- ✅ Progress tracking accurate
- ✅ AI generation functional (if configured)
- ✅ Docker deployment ready
- ✅ Mobile responsive interface

---

## 🎉 Success Criteria

Your installation is successful if:
1. ✅ You can complete all 10 Python exercises
2. ✅ XP and rank update after each completion
3. ✅ Progress persists when you log out and back in
4. ✅ Dashboard shows accurate completion percentage
5. ✅ UI is responsive and animations are smooth
6. ✅ No console errors in browser
7. ✅ No server errors in terminal

Congratulations! Your LearnHub platform is fully functional! 🎓
