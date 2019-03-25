from rest_framework import serializers
from .models import FormGroup, Field
import json


# class JsonSerializer(serializers.JSONField):
#     fields = json.encoder


# class ListSerializer(serializers.ListField):
#     list = serializers.CharField()


class FormGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormGroup
        fields = ('id',
                  'layout',
                  'name',
                  'back_color',
                  'text_color',
                  'created_date', 'updated_date'
                  )


class FieldSerializer(serializers.ModelSerializer):
    # list = ListSerializer()

    class Meta:
        model = Field
        fields = ('id',
                  'form_group',
                  'type',
                  'name',
                  'holder',
                  'value',
                  'url',
                  'list',
                  'width',
                  'back_color',
                  'text_color',
                  'image',
                  'created_date', 'updated_date'
                  )
