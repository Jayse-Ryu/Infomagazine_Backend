from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # Model set
        model = User
        # Field set
        fields = (
            'id',
            'account',
            'email',
            'organization',
            'full_name',
            'phone',
            'password',
            'is_superuser',
            'is_active',
            'is_staff',
            'is_guest',
            'guest_company',
            'last_login',
            'created_date',
            'updated_date'
        )

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        is_active = validated_data.pop('is_active', True)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance
