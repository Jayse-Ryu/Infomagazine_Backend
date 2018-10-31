from rest_framework import serializers
from .models import Form


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = Form
        # 필드 설정
        fields = ('landing_page', 'section', 'title', 'created_date', 'updated_date')
