from rest_framework import serializers
from .models import Form, Link


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        # Set model
        model = Form
        # Set field
        fields = ('id', 'landing_page', 'section', 'title', 'created_date', 'updated_date')


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        # Set model
        model = Link
        # Set field
        fields = ('id', 'landing_page', 'section', 'title', 'content', 'created_date', 'updated_date')
