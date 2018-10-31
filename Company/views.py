from rest_framework import viewsets
from .serializers import CompanySerializer
from .models import Company


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
