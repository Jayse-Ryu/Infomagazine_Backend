from rest_framework import serializers
from .models import Term


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('id',
                  'layout',
                  'title',
                  'content',
                  'image',
                  'created_date', 'updated_date'
                  )
