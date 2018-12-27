from rest_framework import serializers
from .models import GuestFilter


class GuestFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestFilter
        fields = ('id', 'guest', 'company', 'landing')
