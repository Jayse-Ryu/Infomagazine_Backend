import boto3
from decouple import config
from rest_framework.viewsets import ViewSet
from rest_framework import mixins, status
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
import json
import decimal

from boto3.dynamodb.conditions import Key, Attr
from UserAccess.models import UserAccess
from Company.models import Company
from UserAccess.serializers import UserAccessSerializer
from Company.serializers import CompanySerializer


class LandingViewSet(ViewSet, mixins.ListModelMixin):

    def create(self, request):
        req = json.loads(request.body)
        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        dynamo_db = session.resource('dynamodb')

        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = table.put_item(
            Item={
                "LandingName": req['LandingName'],
                "LandingInfo": req['LandingInfo'],
                "LandingTime": req['LandingTime']
            }
        )

        if dynamo_db_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return Response(req, status=status.HTTP_200_OK)
        else:
            return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self):
        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        dynamo_db = session.resource('dynamodb')

        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = json.dumps(table.scan(), cls=DecimalEncoder)

        return Response(json.loads(dynamo_db_res), status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        manager_queryset = UserAccess.objects.all()
        manager_serializer_class = UserAccessSerializer
        company_queryset = Company.objects.all()
        company_serializer_class = CompanySerializer

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        # Filter object along url params
        # Filter object along url params

        # If list searched as user name
        manager = self.request.query_params.get('manager', None)
        if manager is not None:
            manager_queryset = manager_queryset.filter(
                Q(user__full_name__icontains=manager) | Q(user__account__icontains=manager)
            )
            manager_serializer = manager_serializer_class(manager_queryset, many=True)
            print('manager data', manager_serializer.data)
        else:
            print('manager is none')

        company = self.request.query_params.get('company', None)
        if company is not None:
            company_queryset = company_queryset.filter(
                Q(name__icontains=company) | Q(sub_name__icontains=company)
            )
            company_serializer = company_serializer_class(company_queryset, many=True)
            print('company data', company_serializer.data)
        else:
            print('company is none')

        # Url filter done
        # Dynamo filter start

        dynamo_db = session.resource('dynamodb')

        table = dynamo_db.Table('Infomagazine')

        name = self.request.query_params.get('name', None)
        if name is not None:
            name_param = name
            dynamo_db_res = json.dumps(
                table.scan(
                    FilterExpression=Key('LandingName').eq(name_param)
                ),
                cls=DecimalEncoder)

        else:
            dynamo_db_res = json.dumps(table.scan(), cls=DecimalEncoder)

        # for key, value in json.loads(dynamo_db_res):
        #     # print('item', item['Items'])
        #     print(key, value)

        for key, possible_values in json.loads(dynamo_db_res).items():
            # print('item', item['Items'])
            print('key print', key)
            print('possible value', possible_values)
            if 'Items' in key:
                print(key)
                print('inside!')
                break

        return Response(json.loads(dynamo_db_res), status=status.HTTP_200_OK)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# class LandingViewSet(mixins.CreateModelMixin,
#                      mixins.ListModelMixin,
#                      mixins.RetrieveModelMixin,
#                      mixins.UpdateModelMixin,
#                      mixins.DestroyModelMixin,
#                      viewsets.GenericViewSet):
#     queryset = Landing.objects.all().order_by('-created_date')
#     serializer_class = LandingSerializer
#     lookup_field = 'id'
#     # print('Basic view queryset = ', queryset)
#     # permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, headers=headers)
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         # (name = str, company = str, manager = str,)
#         # If list searched as landing page name
#         name = self.request.query_params.get('name', None)
#         if name is not None:
#             queryset = queryset.filter(name__icontains=name)
#
#         # If list searched as company name
#         company = self.request.query_params.get('company', None)
#         if company is not None:
#             queryset = queryset.filter(company__name__icontains=company)
#
#         # If list searched as manager name
#         manager = self.request.query_params.get('manager', None)
#         if manager is not None:
#             queryset = queryset.filter(manager__full_name__icontains=manager)
#
#         # Pagination
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, *args, **kwargs):
#         # print('Retrieve request = ', request)
#         # print('Retrieve args = ', args)
#         # print('Retrieve kwargs = ', kwargs)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#
#     def update(self, request, *args, **kwargs):
#         # print('Update request = ', request)
#         # print('Update args = ', args)
#         # print('Update kwargs = ', kwargs)
#         partial = kwargs.pop('partial = ', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)
#
#     def perform_destroy(self, instance):
#         # print('Delete instance = ', instance)
#         instance.delete()
# class LayoutViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin,
#                     mixins.RetrieveModelMixin,
#                     mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin,
#                     viewsets.GenericViewSet):
#     queryset = Layout.objects.all().order_by('-created_date')
#     serializer_class = LayoutSerializer
#     lookup_field = 'id'
#
#     # print('Basic view queryset = ', queryset)
#     # permission_classes = (IsAuthenticatedOrReadOnly,)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, headers=headers)
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         # If list searched as landing page name
#         name = self.request.query_params.get('name', None)
#         if name is not None:
#             queryset = queryset.filter(name__icontains=name)
#
#         # Search layout list as landing id
#         landing = self.request.query_params.get('landing', None)
#         if landing is not None:
#             queryset = queryset.filter(landing__exact=landing)
#
#         # Pagination
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, *args, **kwargs):
#         # print('Retrieve request = ', request)
#         # print('Retrieve args = ', args)
#         # print('Retrieve kwargs = ', kwargs)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)
#
#     def update(self, request, *args, **kwargs):
#         # print('Update request = ', request)
#         # print('Update args = ', args)
#         # print('Update kwargs = ', kwargs)
#         partial = kwargs.pop('partial = ', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return Response(serializer.data)
#
#     def perform_destroy(self, instance):
#         # print('Delete instance = ', instance)
#         instance.delete()
