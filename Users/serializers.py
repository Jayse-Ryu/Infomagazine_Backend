from rest_framework import serializers
from .models import User  # , Authority


# class AuthoritySerializer(serializers.ModelSerializer):
#     class Meta:
#         # Set model
#         model = Authority
#         # Set fields
#         fields = ('name', 'description')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = User
        # 필드 설정
        fields = ('id', 'username', 'email', 'organization', 'full_name', 'phone', 'password',
                  'is_superuser', 'is_active', 'is_staff', 'last_login', 'created_date', 'updated_date')
