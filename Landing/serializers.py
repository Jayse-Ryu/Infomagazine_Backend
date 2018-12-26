from rest_framework import serializers
from .models import Landing, Layout
import json


class OrderSerializer(serializers.JSONField):
    order = json.encoder


class LandingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Landing
        fields = ('id', 'company', 'manager', 'name', 'title', 'header_script', 'body_script', 'base_url', 'view',
                  'hit', 'is_hijack', 'hijack_url', 'is_mobile', 'is_active',  'created_date', 'updated_date')


class LayoutSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = Layout
        fields = ('id', 'landing', 'order', 'is_banner', 'banner_url', 'banner_url', 'banner_image',
                  'inner_db', 'is_term', 'image_term', 'show_company', 'created_date', 'updated_date')
