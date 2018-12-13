from rest_framework import serializers
from .models import Term, Urls


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('id', 'landing_page', 'title', 'content', 'image', 'is_image', 'created_date', 'updated_date')


class UrlsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Urls
        fields = ('id', 'landing_page', 'url', 'views', 'description', 'created_date', 'updated_date')
