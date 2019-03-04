from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = Video
        # 필드 설정
        fields = ('id', 'type', 'url', 'desc', 'created_date', 'updated_date')
