from rest_framework import viewsets
from .serializers import TermSerializer
from .models import Term


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects
    serializer_class = TermSerializer
