from rest_framework import serializers
from .models import Collection
import json


class DataSerializer(serializers.JSONField):
    data = json.encoder


class CollectionSerializer(serializers.ModelSerializer):
    data = DataSerializer()

    class Meta:
        # 모델 설정
        model = Collection
        # 필드 설정
        fields = ('id', 'landing', 'data', 'url', 'form_group', 'created_date', 'updated_date')
