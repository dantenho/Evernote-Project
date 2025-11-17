"""
URL configuration for learning app API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    UserProfileView,
    logout_view,
    LearningPathViewSet,
    UserProgressViewSet,
    complete_step,
    my_progress,
    my_achievements,
    available_achievements,
    user_profile_gamification,
    generate_code_hint,
)
from . import ai_views

router = DefaultRouter()
router.register(r'learning-paths', LearningPathViewSet, basename='learning-path')
router.register(r'progress', UserProgressViewSet, basename='user-progress')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # User progress endpoints
    path('my-progress/', my_progress, name='my-progress'),
    path('steps/<int:step_id>/complete/', complete_step, name='complete-step'),

    # Gamification endpoints
    path('my-achievements/', my_achievements, name='my-achievements'),
    path('achievements/', available_achievements, name='available-achievements'),
    path('profile/gamification/', user_profile_gamification, name='profile-gamification'),

    # AI Content Generation endpoints
    path('ai/providers/', ai_views.list_ai_providers, name='ai-providers'),
    path('ai/templates/', ai_views.list_content_templates, name='ai-templates'),
    path('ai/generate/lesson/', ai_views.generate_step_lesson, name='ai-generate-lesson'),
    path('ai/generate/quiz/', ai_views.generate_quiz_questions, name='ai-generate-quiz'),
    path('ai/generate/hint/', generate_code_hint, name='ai-generate-hint'),
    path('ai/history/', ai_views.generation_history, name='ai-history'),
    path('ai/history/<int:generation_id>/', ai_views.generation_detail, name='ai-history-detail'),

    # Router URLs (learning-paths, progress)
    path('', include(router.urls)),
]
