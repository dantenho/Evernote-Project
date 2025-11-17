# API Documentation - Duolingo-Style Learning App

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication

This API uses JWT (JSON Web Token) authentication. Most endpoints require authentication except where noted.

### Headers
For authenticated requests, include:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
Create a new user account and receive JWT tokens.

**Endpoint:** `POST /api/v1/auth/register/`
**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-11-17T12:00:00Z"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Validation Rules:**
- `username`: Required, unique
- `email`: Required, unique, valid email format
- `password`: Required, must pass Django password validation
- `password2`: Must match `password`
- `first_name`: Required
- `last_name`: Required

---

### Login
Obtain JWT access and refresh tokens.

**Endpoint:** `POST /api/v1/auth/login/`
**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Refresh Token
Get a new access token using a refresh token.

**Endpoint:** `POST /api/v1/auth/refresh/`
**Authentication:** Not required

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Logout
Blacklist a refresh token (requires token blacklist to be enabled).

**Endpoint:** `POST /api/v1/auth/logout/`
**Authentication:** Required

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "detail": "Successfully logged out."
}
```

---

### Get/Update Profile
View or update the current user's profile.

**Endpoint:** `GET/PATCH /api/v1/auth/profile/`
**Authentication:** Required

**GET Response:** `200 OK`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2025-11-17T12:00:00Z"
}
```

**PATCH Request Body:**
```json
{
  "first_name": "Jonathan",
  "last_name": "Doe",
  "email": "jonathan@example.com"
}
```

**Note:** `username` cannot be updated.

---

## Learning Content Endpoints

### Get Learning Paths
Retrieve all learning areas with nested topics, tracks, steps, and quizzes.

**Endpoint:** `GET /api/v1/learning-paths/`
**Authentication:** Not required (public access)

**Response:** `200 OK`
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Python Programming",
      "order": 1,
      "topics": [
        {
          "id": 1,
          "title": "Python Basics",
          "order": 1,
          "tracks": [
            {
              "id": 1,
              "title": "Getting Started",
              "order": 1,
              "steps": [
                {
                  "id": 1,
                  "title": "Introduction to Python",
                  "content_type": "lesson",
                  "text_content": "Python is a high-level programming language...",
                  "video_url": "https://example.com/video.mp4",
                  "order": 1,
                  "questions": []
                },
                {
                  "id": 2,
                  "title": "Python Basics Quiz",
                  "content_type": "quiz",
                  "text_content": "Test your knowledge...",
                  "video_url": null,
                  "order": 2,
                  "questions": [
                    {
                      "id": 1,
                      "text": "What is Python?",
                      "choices": [
                        {
                          "id": 1,
                          "text": "A programming language",
                          "is_correct": true
                        },
                        {
                          "id": 2,
                          "text": "A snake",
                          "is_correct": false
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Features:**
- Fully nested structure: Area → Topic → Track → Step → Questions → Choices
- Ordered by `order` field at each level
- Optimized queries (uses `prefetch_related` to prevent N+1)
- Pagination (20 items per page by default)

---

## User Progress Endpoints

### Get My Progress
Retrieve all progress for the authenticated user.

**Endpoint:** `GET /api/v1/my-progress/`
**Authentication:** Required

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "step": {
      "id": 1,
      "title": "Introduction to Python",
      "content_type": "lesson",
      "text_content": "Python is...",
      "video_url": "https://example.com/video.mp4",
      "order": 1,
      "questions": []
    },
    "status": "completed",
    "completed_at": "2025-11-17T14:30:00Z",
    "created_at": "2025-11-17T12:00:00Z",
    "updated_at": "2025-11-17T14:30:00Z"
  }
]
```

---

### Complete a Step
Mark a specific step as completed.

**Endpoint:** `POST /api/v1/steps/<step_id>/complete/`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "detail": "Step marked as completed.",
  "progress": {
    "id": 1,
    "step": 1,
    "step_title": "Introduction to Python",
    "step_type": "lesson",
    "track_title": "Getting Started",
    "status": "completed",
    "completed_at": "2025-11-17T14:30:00Z",
    "created_at": "2025-11-17T12:00:00Z",
    "updated_at": "2025-11-17T14:30:00Z"
  }
}
```

**Behavior:**
- Creates progress record if it doesn't exist
- Updates existing record to "completed"
- Sets `completed_at` timestamp
- Idempotent (can be called multiple times)

---

### Get Progress Summary
Retrieve progress statistics for the authenticated user.

**Endpoint:** `GET /api/v1/progress/summary/`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "total_steps": 25,
  "completed_steps": 15,
  "in_progress_steps": 10,
  "completion_percentage": 60.0,
  "areas": [
    {
      "id": 1,
      "title": "Python Programming",
      "total_steps": 15,
      "completed_steps": 10,
      "in_progress_steps": 5,
      "completion_percentage": 66.67
    },
    {
      "id": 2,
      "title": "JavaScript",
      "total_steps": 10,
      "completed_steps": 5,
      "in_progress_steps": 5,
      "completion_percentage": 50.0
    }
  ]
}
```

---

### List User Progress (Paginated)
Get paginated list of user progress records.

**Endpoint:** `GET /api/v1/progress/`
**Authentication:** Required

**Response:** `200 OK`
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/progress/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "step": 1,
      "step_title": "Introduction to Python",
      "step_type": "lesson",
      "track_title": "Getting Started",
      "status": "completed",
      "completed_at": "2025-11-17T14:30:00Z",
      "created_at": "2025-11-17T12:00:00Z",
      "updated_at": "2025-11-17T14:30:00Z"
    }
  ]
}
```

---

### Create Progress Record
Manually create a progress record for a step.

**Endpoint:** `POST /api/v1/progress/`
**Authentication:** Required

**Request Body:**
```json
{
  "step": 5,
  "status": "in_progress"
}
```

**Response:** `201 Created`
```json
{
  "id": 10,
  "step": 5,
  "step_title": "Variables and Types",
  "step_type": "lesson",
  "track_title": "Python Basics",
  "status": "in_progress",
  "completed_at": null,
  "created_at": "2025-11-17T15:00:00Z",
  "updated_at": "2025-11-17T15:00:00Z"
}
```

**Note:** User is automatically set to the authenticated user.

---

### Update Progress Record
Update the status of an existing progress record.

**Endpoint:** `PATCH /api/v1/progress/<progress_id>/`
**Authentication:** Required

**Request Body:**
```json
{
  "status": "completed"
}
```

**Response:** `200 OK`
```json
{
  "id": 10,
  "step": 5,
  "step_title": "Variables and Types",
  "step_type": "lesson",
  "track_title": "Python Basics",
  "status": "completed",
  "completed_at": null,
  "created_at": "2025-11-17T15:00:00Z",
  "updated_at": "2025-11-17T15:05:00Z"
}
```

---

## Data Models

### Area
Top-level learning category.

**Fields:**
- `id` (integer): Unique identifier
- `title` (string): Area name
- `order` (integer): Display order
- `topics` (array): Nested topics

### Topic
Subject within an area.

**Fields:**
- `id` (integer): Unique identifier
- `title` (string): Topic name
- `order` (integer): Display order
- `tracks` (array): Nested tracks

### Track
Learning path within a topic.

**Fields:**
- `id` (integer): Unique identifier
- `title` (string): Track name
- `order` (integer): Display order
- `steps` (array): Nested steps

### Step
Individual lesson or quiz.

**Fields:**
- `id` (integer): Unique identifier
- `title` (string): Step title
- `content_type` (string): Either `"lesson"` or `"quiz"`
- `text_content` (string, nullable): Lesson content
- `video_url` (string, nullable): Video URL
- `order` (integer): Display order
- `questions` (array): Quiz questions (empty for lessons)

### Question
Quiz question.

**Fields:**
- `id` (integer): Unique identifier
- `text` (string): Question text
- `choices` (array): Answer choices

### Choice
Multiple choice answer.

**Fields:**
- `id` (integer): Unique identifier
- `text` (string): Choice text
- `is_correct` (boolean): Whether this is the correct answer

### UserProgress
User's progress on a step.

**Fields:**
- `id` (integer): Unique identifier
- `step` (integer): Step ID
- `status` (string): Either `"completed"` or `"in_progress"`
- `completed_at` (datetime, nullable): Completion timestamp
- `created_at` (datetime): Record creation time
- `updated_at` (datetime): Last update time

---

## Error Responses

### 400 Bad Request
Invalid input data.

```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
Missing or invalid authentication.

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
Resource doesn't exist.

```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
Server error.

```json
{
  "detail": "Internal server error."
}
```

---

## Pagination

List endpoints return paginated results:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/endpoint/?page=3",
  "previous": "http://localhost:8000/api/v1/endpoint/?page=1",
  "results": [...]
}
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Example: `GET /api/v1/learning-paths/?page=2&page_size=10`

---

## JWT Token Lifetimes

- **Access Token:** 1 hour
- **Refresh Token:** 7 days

Refresh tokens are rotated on each refresh request for security.

---

## CORS Configuration

The API allows requests from:
- `http://localhost:5173` (Vite)
- `http://localhost:3000` (Vue CLI)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

Credentials (cookies, authorization headers) are allowed.

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting in production.

---

## Example Workflows

### 1. User Registration and First Lesson

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "learner1",
    "email": "learner@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "Jane",
    "last_name": "Learner"
  }'

# Response includes access token
# Save the access token

# Get learning paths
curl http://localhost:8000/api/v1/learning-paths/

# Complete first step
curl -X POST http://localhost:8000/api/v1/steps/1/complete/ \
  -H "Authorization: Bearer <access_token>"

# Check progress
curl http://localhost:8000/api/v1/my-progress/ \
  -H "Authorization: Bearer <access_token>"
```

### 2. Track Progress Across Multiple Areas

```bash
# Complete steps in different areas
curl -X POST http://localhost:8000/api/v1/steps/5/complete/ \
  -H "Authorization: Bearer <access_token>"

curl -X POST http://localhost:8000/api/v1/steps/10/complete/ \
  -H "Authorization: Bearer <access_token>"

# Get summary with breakdown by area
curl http://localhost:8000/api/v1/progress/summary/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Testing

All endpoints have comprehensive integration tests. Run tests with:

```bash
python -m pytest learning/tests/
```

Current test coverage: **95%**

---

## Future Enhancements

Potential additions for Phase 2:

1. **Quiz Submission**: POST endpoint to submit quiz answers and get results
2. **Leaderboards**: User rankings based on progress
3. **Achievements/Badges**: Unlock achievements for milestones
4. **Learning Streaks**: Track consecutive days of learning
5. **Prerequisites**: Enforce track/step prerequisites
6. **User Stats**: Detailed analytics dashboard
7. **Social Features**: Follow other learners, share progress
8. **Search**: Search for specific topics or content
9. **Recommendations**: Personalized learning path suggestions
10. **Mobile API**: Optimized endpoints for mobile apps
