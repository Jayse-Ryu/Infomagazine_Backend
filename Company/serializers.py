from rest_framework import serializers
from .models import Company  # , GuestFilter


class CompanySerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField(required=False, default='비어있음')
    organization_name = serializers.SerializerMethodField(required=False, default='비어있음')

    def get_manager_name(self, obj):
        if obj.manager is not None:
            return str(obj.manager.full_name)
        else:
            return '비어있음'

    def get_organization_name(self, obj):
        if obj.organization is not None:
            return str(obj.organization.name)
        else:
            return '비어있음'

    class Meta:
        model = Company
        fields = ('id', 'manager', 'manager_name', 'name', 'sub_name', 'header', 'address', 'corp_num',
                  'phone', 'email', 'desc', 'organization', 'organization_name',
                  'created_date', 'updated_date')
