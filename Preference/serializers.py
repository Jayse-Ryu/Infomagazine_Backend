from rest_framework import serializers
from .models import Term, Url


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('id', 'landing', 'title', 'content', 'image', 'created_date', 'updated_date')


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ('id', 'landing', 'url', 'desc', 'view', 'hit', 'created_date', 'updated_date')
