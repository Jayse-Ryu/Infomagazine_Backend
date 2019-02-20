from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField(required=False, default='비어있음')

    def get_organization_name(self, obj):
        if obj.organization is not None:
            return str(obj.organization.name)
        else:
            return '비어있음'

    class Meta:
        model = Company
        fields = ('id',
                  'organization', 'organization_name',
                  'name', 'sub_name',
                  'header',
                  'address',
                  'corp_num',
                  'phone',
                  'email',
                  'desc',
                  'created_date', 'updated_date'
                  )
