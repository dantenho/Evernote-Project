from rest_framework import serializers
from .models import Area, Topico, Trilha

class TrilhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trilha
        fields = ['title', 'order']

class TopicoSerializer(serializers.ModelSerializer):
    tracks = TrilhaSerializer(many=True, read_only=True)

    class Meta:
        model = Topico
        fields = ['title', 'order', 'tracks']

class AreaSerializer(serializers.ModelSerializer):
    topics = TopicoSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['title', 'order', 'topics']
