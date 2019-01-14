from rest_framework import serializers
from .models import Landing, Layout
import json


class OrderSerializer(serializers.JSONField):
    order = json.encoder


class LandingSerializer(serializers.ModelSerializer):

    company_name = serializers.SerializerMethodField(required=False, default='비어있음')
    manager_name = serializers.SerializerMethodField(required=False, default='비어있음')

    def get_company_name(self, obj):
        if obj.company is not None:
            return str(obj.company.name)
        else:
            return '비어있음'

    def get_manager_name(self, obj):
        if obj.manager is not None:
            return str(obj.manager.full_name)
        else:
            return '비어있음'

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
