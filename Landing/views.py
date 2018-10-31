from rest_framework import viewsets
from .serializers import LandingSerializer
from .models import Landing


class LandingViewSet(viewsets.ModelViewSet):
    queryset = Landing.objects.all()
    serializer_class = LandingSerializer


