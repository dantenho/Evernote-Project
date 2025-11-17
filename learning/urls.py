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
)

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

    # Router URLs (learning-paths, progress)
    path('', include(router.urls)),
]
