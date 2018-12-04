from rest_framework import serializers
from .models import Files


class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = Files
        # 필드 설정
        fields = ('id', 'landing_page', 'file', 'created_date', 'updated_date')
