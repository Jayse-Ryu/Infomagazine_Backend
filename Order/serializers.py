from rest_framework import serializers
from .models import Order
from Form.serializers import FormGroupSerializer
from Video.serializers import VideoSerializer
from Files.serializers import ImageSerializer


class OrderSerializer(serializers.ModelSerializer):

    item = serializers.SerializerMethodField(required=False, default='')

    def get_item(self, obj):
        if obj.type is 0:
            return ImageSerializer()
        elif obj.type is 1:
            return FormGroupSerializer()
        elif obj.type is 2:
            return VideoSerializer()
        else:
            return '비었음'

    class Meta:
        model = Order
        fields = (
            'id', 'layout', 'position', 'type', 'item', 'created_date', 'updated_date',
            )
