from rest_framework import viewsets
from .serializers import LandingSerializer, LayoutSerializer
from .models import Landing, Layout


class LandingViewSet(viewsets.ModelViewSet):
    queryset = Landing.objects.all()
    serializer_class = LandingSerializer


class LayoutViewSet(viewsets.ModelViewSet):
    queryset = Layout.objects.all()
    serializer_class = LayoutSerializer
