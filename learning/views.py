from rest_framework import generics
from .models import Area
from .serializers import AreaSerializer

class LearningPathListAPIView(generics.ListAPIView):
    """
    API view to retrieve the entire nested learning path structure.
    """
    serializer_class = AreaSerializer

    def get_queryset(self):
        """
        Optimize the queryset by prefetching related topics and tracks
        to avoid the N+1 query problem.
        """
        return Area.objects.prefetch_related('topics__tracks').all()
