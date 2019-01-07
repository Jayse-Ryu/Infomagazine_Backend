from rest_framework import serializers
from .models import Company  # , GuestFilter


class CompanySerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()

    def get_manager_name(self, obj):
        return str(obj.manager.full_name)

    class Meta:
        model = Company
        fields = ('id', 'manager', 'manager_name', 'name', 'sub_name', 'header', 'address', 'corp_num', 'phone',
                  'email', 'desc', 'created_date', 'updated_date')
