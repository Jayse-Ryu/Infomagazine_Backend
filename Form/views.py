from rest_framework import viewsets
from .serializers import FormSerializer
from .models import Form


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
