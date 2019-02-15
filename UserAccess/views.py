from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.db.models import Q
from .models import UserAccess
from .serializers import UserAccessSerializer
from Users.models import User
from itertools import chain


class UserAccessViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = UserAccess.objects.all().order_by('-updated_date')
    serializer_class = UserAccessSerializer
    lookup_field = 'user'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user = User.objects.all().order_by('-updated_date')

        # If list searched as user name
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(user__full_name__icontains=name)

        # as user id
        user = self.request.query_params.get('user', None)
        if user is not None:
            queryset = queryset.filter(user_id__exact=user)

        account = self.request.query_params.get('account', None)
        if account is not None:
            queryset = queryset.filter(user__account__icontains=account)

        # as organization id
        organization = self.request.query_params.get('organization', None)
        if organization is not None:
            queryset = queryset.filter(organization__exact=organization)

        # as organization name
        org_name = self.request.query_params.get('org_name', None)
        if org_name is not None:
            queryset = queryset.filter(organization_name__icontains=org_name)

        # company id
        company = self.request.query_params.get('company', None)
        if company is not None:
            queryset = queryset.filter(company__exact=company)

        # company name
        com_name = self.request.query_params.get('com_name', None)
        if com_name is not None:
            queryset = queryset.filter(company_name__icontains=com_name)

        # merge_user = self.request.query_params.get('merge_user', None)
        # if merge_user is not None:
        #     queryset = list(chain(queryset, user))

        sort = self.request.query_params.get('sort', None)
        if sort is not None:
            queryset = queryset.order_by('-created_date')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # print('Update request = ', request)
        # print('Update args = ', args)
        # print('Update kwargs = ', kwargs)
        partial = kwargs.pop('partial = ', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # print('Patch request = ', request)
        # print('Patch args = ', args)
        # print('Patch kwargs = ', kwargs)
        kwargs['partial'] = True
        partial = kwargs.pop('partial = ', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        # print('Delete instance = ', instance)
        instance.delete()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
