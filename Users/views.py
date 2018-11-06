from rest_framework import viewsets
from .serializers import UserSerializer  # AuthoritySerializer
from .models import User  # Authority


# class AuthorityViewSet(viewsets.ModelViewSet):
#     queryset = Authority.objects.all()
#     serializer_class = AuthoritySerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
