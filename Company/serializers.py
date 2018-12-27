from rest_framework import serializers
from .models import Company  # , GuestFilter


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        # 모델 설정
        model = Company
        # 필드 설정
        fields = ('id', 'manager', 'name', 'sub_name', 'header', 'address', 'corp_num', 'phone',
                  'email', 'desc', 'created_date', 'updated_date')
