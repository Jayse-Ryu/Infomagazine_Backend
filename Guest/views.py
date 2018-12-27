from rest_framework import viewsets
from .models import GuestFilter
from .serializers import GuestFilterSerializer


class GuestFilterViewSet(viewsets.ModelViewSet):
    queryset = GuestFilter.objects.all()
    serializer_class = GuestFilterSerializer
