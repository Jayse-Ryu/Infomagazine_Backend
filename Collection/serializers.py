from rest_framework import serializers
from .models import Collections


class CollectionsSerializer(serializers.ModelSerializer):
    data = serializers.ListField(
        required=True,
        child=serializers.CharField(allow_blank=True)
    )

    class Meta:
        # 모델 설정
        model = Collections
        # 필드 설정
        fields = ('id', 'landing_page', 'data', 'created_date', 'updated_date')
