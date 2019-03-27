from rest_framework import viewsets, mixins
from .serializers import TermSerializer
from rest_framework.response import Response
from django.db.models import Q
from .models import Term


# class TermViewSet(viewsets.ModelViewSet):
#     queryset = Term.objects
#     serializer_class = TermSerializer


class TermViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Term.objects.all().order_by('-created_date')
    serializer_class = TermSerializer
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        layout = self.request.query_params.get('layout', None)
        if layout is not None:
            queryset = queryset.filter(layout__exact=layout)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # print('Retrieve request = ', request)
        # print('Retrieve args = ', args)
        # print('Retrieve kwargs = ', kwargs)
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
        # kwargs['full_name'] = True
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
