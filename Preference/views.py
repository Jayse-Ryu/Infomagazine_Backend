from rest_framework import viewsets
from .serializers import TermSerializer, UrlSerializer
from .models import Term, Url


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects
    serializer_class = TermSerializer


class UrlViewSet(viewsets.ModelViewSet):
    queryset = Url.objects.all()
    serializer_class = UrlSerializer
