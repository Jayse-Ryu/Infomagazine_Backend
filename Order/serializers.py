from rest_framework import serializers
from .models import Order
from Form.serializers import FormGroupSerializer
from Video.serializers import VideoSerializer
from Files.serializers import ImageSerializer
import json


class PositionSerializer(serializers.JSONField):
    position = json.encoder


class OrderSerializer(serializers.ModelSerializer):
    position = PositionSerializer()
    item = serializers.SerializerMethodField(required=False, default='')
    # type always 0 temporary

    def get_item(self, obj):
        if obj.type is 1:
            return ImageSerializer()
        elif obj.type is 2:
            return FormGroupSerializer()
        elif obj.type is 3:
            return VideoSerializer()
        else:
            return '비었음'

    class Meta:
        model = Order
        fields = (
            'id',
            'layout',
            'name',
            'position',
            'type',
            'item',
            'created_date', 'updated_date'
        )
