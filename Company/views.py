from rest_framework import viewsets
from .models import Company  # , GuestFilter
from .serializers import CompanySerializer  # , GuestFilterSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
