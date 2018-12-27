from rest_framework import viewsets
from .serializers import UrlSerializer
from .models import Url


class UrlViewSet(viewsets.ModelViewSet):
    queryset = Url.objects.all()
    serializer_class = UrlSerializer
