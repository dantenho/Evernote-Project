from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Area, Topico, Trilha

class LearningPathAPITest(APITestCase):
    def setUp(self):
        """
        Set up the data for the test.
        """
        self.area = Area.objects.create(title="Programação", order=1)
        self.topic = Topico.objects.create(title="Python", area=self.area, order=1)
        self.track = Trilha.objects.create(title="Básico", topic=self.topic, order=1)

    def test_get_learning_path_list(self):
        """
        Ensure we can retrieve the nested learning path list.
        """
        url = reverse('learning-path-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Check area level
        area_data = response.data[0]
        self.assertEqual(area_data['title'], "Programação")
        self.assertEqual(len(area_data['topics']), 1)

        # Check topic level
        topic_data = area_data['topics'][0]
        self.assertEqual(topic_data['title'], "Python")
        self.assertEqual(len(topic_data['tracks']), 1)

        # Check track level
        track_data = topic_data['tracks'][0]
        self.assertEqual(track_data['title'], "Básico")
