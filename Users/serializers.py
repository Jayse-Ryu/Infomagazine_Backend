from rest_framework import serializers
from .models import Authority, Users


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        # Set model
        model = Authority
        # Set fields
        fields = ('name', 'description')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = Users
        # 필드 설정
        fields = ('account', 'name', 'organization', 'email', 'phone', 'authority', 'password', 'created_date', 'updated_date')
