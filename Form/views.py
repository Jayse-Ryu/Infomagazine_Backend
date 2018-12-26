from rest_framework import viewsets
from .models import FormGroup, Field
from .serializers import FormGroupSerializer, FieldSerializer


class FormGroupViewSet(viewsets.ModelViewSet):
    queryset = FormGroup.objects.all()
    serializer_class = FormGroupSerializer


class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
