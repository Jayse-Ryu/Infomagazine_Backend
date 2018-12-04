from rest_framework import serializers
from .models import Landing


class LandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landing
        fields = ('id', 'company', 'name', 'title', 'status', 'header_script', 'body_script',
                  'mobile_only', 'image_switch', 'views', 'hits', 'created_date', 'updated_date')
