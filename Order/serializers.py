# from rest_framework import serializers
# from .models import Order
# import json
#
#
# class PositionSerializer(serializers.JSONField):
#     position = json.encoder
#
#
# class OrderSerializer(serializers.ModelSerializer):
#     position = PositionSerializer()
#
#     class Meta:
#         model = Order
#         fields = (
#             'id',
#             'layout',
#             'name',
#             'position',
#             'type',
#             'image',
#             'form_group',
#             'video',
#             'created_date', 'updated_date'
#         )
