from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.db.models import Q
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Company.objects.all().order_by('-created_date')
    serializer_class = CompanySerializer
    lookup_field = 'id'
    # print('Basic view queryset = ', queryset)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # (name = str, manager = str,)
        # If list searched as company name or sub_name
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(Q(name__icontains=name) | Q(sub_name__icontains=name))

        # If list searched as manager name
        manager = self.request.query_params.get('manager', None)
        if manager is not None:
            queryset = queryset.filter(manager__full_name__icontains=manager)

        company = self.request.query_params.get('company', None)
        if company is not None:
            queryset = queryset.filter(company__exact=company)

        organization = self.request.query_params.get('organization', None)
        if organization is not None:
            queryset = queryset.filter(organization__exact=organization)

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

    def perform_destroy(self, instance):
        # print('Delete instance = ', instance)
        instance.delete()
