from rest_framework import viewsets
from .serializers import AuthoritySerializer, UsersSerializer
from .models import Authority, Users


class AuthorityViewSet(viewsets.ModelViewSet):
    queryset = Authority.objects.all()
    serializer_class = AuthoritySerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
