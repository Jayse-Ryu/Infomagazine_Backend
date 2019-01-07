from rest_framework import serializers
from .models import Landing, Layout
import json


class OrderSerializer(serializers.JSONField):
    order = json.encoder


class LandingSerializer(serializers.ModelSerializer):

    company_name = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    def get_company_name(self, obj):
        return str(obj.company.name)

    def get_manager_name(self, obj):
        return str(obj.manager.full_name)

    class Meta:
        model = Landing
        fields = (
            'id', 'company', 'company_name', 'manager', 'manager_name', 'name', 'title',
            'header_script', 'body_script', 'base_url', 'view', 'hit', 'is_hijack', 'hijack_url',
            'is_mobile', 'is_active',  'created_date', 'updated_date',
            )


class LayoutSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = Layout
        fields = ('id', 'landing', 'order', 'is_banner', 'banner_url', 'banner_url', 'banner_image',
                  'inner_db', 'font', 'is_term', 'image_term', 'show_company', 'created_date', 'updated_date')
