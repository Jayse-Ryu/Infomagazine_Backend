from rest_framework import viewsets
from .serializers import CollectionsSerializer
from .models import Collections


class CollectionsViewSet(viewsets.ModelViewSet):
    queryset = Collections.objects.all()
    serializer_class = CollectionsSerializer
