from rest_framework import serializers
from .models import UserAccess
# from Users.models import User
# from Users.serializers import UserSerializer


class UserAccessSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField(required=False, default='비어있음')
    user_name = serializers.SerializerMethodField(required=False, default='비어있음')
    organization_name = serializers.SerializerMethodField(required=False, default='비어있음')
    company_name = serializers.SerializerMethodField(required=False, default='비어있음')
    phone = serializers.SerializerMethodField(required=False, default='비어있음')
    email = serializers.SerializerMethodField(required=False, default='비어있음')

    def get_account(self, obj):
        if obj.user is not None:
            return str(obj.user.account)
        else:
            return '비어있음'

    def get_user_name(self, obj):
        if obj.user is not None:
            return str(obj.user.full_name)
        else:
            return '비어있음'

    def get_organization_name(self, obj):
        if obj.organization is not None:
            return str(obj.organization.name)
        else:
            return '비어있음'

    def get_company_name(self, obj):
        if obj.company is not None:
            return str(obj.company.name)
        else:
            return '비어있음'

    def get_phone(self, obj):
        if obj.user.phone is not None:
            return str(obj.user.phone)
        else:
            return '비어있음'

    def get_email(self, obj):
        if obj.user.email is not None:
            return str(obj.user.email)
        else:
            return '비어있음'

    class Meta:  # 'organization_name', 'company_name',
        model = UserAccess
        fields = ('user', 'access', 'organization', 'company',
                  'account', 'user_name', 'organization_name', 'company_name', 'phone', 'email',
                  'created_date', 'updated_date')
        # fields = ('user', 'access', 'organization', 'company',
        #           'created_date', 'updated_date')

    # def create(self, validated_data):
    #     user_data = validated_data.pop('user')
    #     user = UserSerializer.create(UserSerializer(), validated_data=user_data)
    #     user_name, created_date = UserAccess.objects.update_or_create(user=user, access=validated_data.pop('access'))
    #     return user_name
