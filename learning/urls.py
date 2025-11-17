from django.urls import path
from .views import LearningPathListAPIView

urlpatterns = [
    path('learning-paths/', LearningPathListAPIView.as_view(), name='learning-path-list'),
]
