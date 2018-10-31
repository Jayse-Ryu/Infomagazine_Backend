from rest_framework import viewsets
from .serializers import TermSerializer, UrlsSerializer
from .models import Term, Urls


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects
    serializer_class = TermSerializer


class UrlsViewSet(viewsets.ModelViewSet):
    queryset = Urls.objects.all()
    serializer_class = UrlsSerializer
