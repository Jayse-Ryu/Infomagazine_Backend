from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import Collection
from .serializers import CollectionSerializer


class CollectionViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Collection.objects.all().order_by('-created_date')
    serializer_class = CollectionSerializer
    lookup_field = 'id'
    print('Basic view queryset = ', queryset)

    def create(self, request, *args, **kwargs):
        print('Create request = ', request)
        print('Create args = ', args)
        print('Create kwargs = ', kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)

    def list(self, request, *args, **kwargs):
        print('List request = ', request)
        print('List args = ', args)
        print('List args = ', kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        print('Retrieve request = ', request)
        print('Retrieve args = ', args)
        print('Retrieve kwargs = ', kwargs)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        print('Update request = ', request)
        print('Update args = ', args)
        print('Update kwargs = ', kwargs)
        partial = kwargs.pop('partial = ', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        print('Delete instance = ', instance)
        instance.delete()
