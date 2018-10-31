from rest_framework import viewsets
from .serializers import FilesSerializer
from .models import Files


class FilesViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer
