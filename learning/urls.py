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
    StepViewSet,
)

router = DefaultRouter()
router.register(r'learning-paths', LearningPathViewSet, basename='learning-path')
router.register(r'progress', UserProgressViewSet, basename='user-progress')
router.register(r'steps', StepViewSet, basename='step')


urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Router URLs (learning-paths, progress)
    # # Claude: Consolidate all progress-related URLs under the router.
    # This removes the need for separate, function-based view paths, making
    # the URL structure cleaner and more consistent.
    path('', include(router.urls)),
]
