from rest_framework import serializers
from .models import UserAccess  # , GuestFilter


class UserAcessSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(required=False, default='비어있음')
    organization_name = serializers.SerializerMethodField(required=False, default='비어있음')
    company_name = serializers.SerializerMethodField(required=False, default='비어있음')

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

    class Meta:
        model = UserAccess
        fields = ('id', 'user', 'user_name', 'access', 'organization', 'organization_name', 'company', 'company_name',
                  'created_date', 'updated_date')
