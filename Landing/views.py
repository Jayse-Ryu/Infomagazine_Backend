import boto3
import botocore
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


class LandingViewSet(ViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

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
                "LandingNum": req['LandingNum']
            }
        )

        if dynamo_db_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return Response(req, status=status.HTTP_200_OK)
        else:
            return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        # print('get self', self)
        # print('get req', request)
        # print('get args', args)
        # print('get kwarg', kwargs)

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

    def retrieve(self, request, *args, **kwargs):

        sign_param = json.loads(kwargs['pk'])

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = json.dumps(table.scan(
            FilterExpression=Key('LandingNum').eq(sign_param)
        ), cls=DecimalEncoder)

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
        manager_filter = []
        manager = self.request.query_params.get('manager', None)
        if manager is not None:
            manager_queryset = manager_queryset.filter(
                Q(user__full_name__icontains=manager) | Q(user__account__icontains=manager)
            )
            manager_serializer = manager_serializer_class(manager_queryset, many=True)
            for mans in manager_serializer.data:
                manager_filter.append(int(json.dumps(mans['user'])))

        # If list searched as company name
        company_filter = []
        company = self.request.query_params.get('company', None)
        if company is not None:
            company_queryset = company_queryset.filter(
                Q(name__icontains=company) | Q(sub_name__icontains=company)
            )
            company_serializer = company_serializer_class(company_queryset, many=True)
            for coms in company_serializer.data:
                company_filter.append(int(json.dumps(coms['id'])))
        # Url filter done
        # Url filter done

        # Dynamo filter start
        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        # Dynamo filter
        # Dynamo filter
        sign = self.request.query_params.get('sign', None)
        name = self.request.query_params.get('name', None)

        if sign is not None:
            sign_param = sign
            dynamo_db_res = json.dumps(
                table.scan(
                    FilterExpression=Key('LandingNum').eq(sign_param)
                ),
                cls=DecimalEncoder
            )
        elif name is not None:
            name_param = name
            dynamo_db_res = json.dumps(
                table.scan(
                    FilterExpression=Attr('LandingName').contains(name_param)
                ),
                cls=DecimalEncoder
            )
        elif len(manager_filter) is not 0:
            dynamo_db_res = json.dumps(
                table.scan(
                    FilterExpression=Attr('LandingInfo.landing.manager').is_in(manager_filter)
                ),
                cls=DecimalEncoder
            )
        elif len(company_filter) is not 0:
            dynamo_db_res = json.dumps(
                table.scan(
                    FilterExpression=Attr('LandingInfo.landing.company').is_in(company_filter)
                ),
                cls=DecimalEncoder
            )
        else:
            dynamo_db_res = json.dumps(table.scan(), cls=DecimalEncoder)
        # Dynamo filter end
        # Dynamo filter end

        dynamo_obj = json.loads(dynamo_db_res)
        # Add manager, company name in landing table
        for key, possible_values in dynamo_obj.items():
            # Stop for at 'Item' section
            if 'Items' in key:
                # Inside of 'Items'
                for section in possible_values:
                    get_manger = self.get_manager(section['LandingInfo']['landing']['manager'])
                    get_company = self.get_company(section['LandingInfo']['landing']['company'])
                    section['LandingInfo']['landing']['manager_name'] = get_manger
                    section['LandingInfo']['landing']['company_name'] = get_company
            break

        # print('result dynamo db is ', dynamo_obj['Items'])

        return Response(dynamo_obj, status=status.HTTP_200_OK)

    def get_manager(self, *args):
        manager_queryset = UserAccess.objects.all()
        manager_serializer_class = UserAccessSerializer

        manager_queryset = manager_queryset.filter(user__exact=args[0])
        manager_serializer = manager_serializer_class(manager_queryset, many=True)
        for item in manager_serializer.data:
            return item['user_name']

    def get_company(self, *args):
        company_queryset = Company.objects.all()
        company_serializer_class = CompanySerializer

        company_queryset = company_queryset.filter(id__exact=args[0])
        company_serializer = company_serializer_class(company_queryset, many=True)
        for item in company_serializer.data:
            return item['name']


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# landing views: view has to be a number
# landing collection: has to blank list

# term image: empty list?

# field type: why string? i want number

# order image url none parse


req_body_chk = {
    'LandingName': 'full landing',
    'LandingTime': 1554788867806,
    'LandingInfo': {
        'landing': {
            'company': 1,
            'manager': 2,
            'name': 'full landing',
            'title': 'page title is',
            'header_script': 'header is ',
            'body_script': 'body is ',
            'base_url': 'full',
            'is_hijack': False,
            'hijack_url': None,
            'is_active': True,
            'is_mobile': False,
            # view has to be a number done
            'views': None,
            # has to blank list done
            'collections': None,
            'is_banner': False,
            'banner_url': None,
            'banner_image': None,
            'inner_db': True,
            'font': -1,
            'is_term': True,
            'image_term': False,
            'show_company': False
        },
        'term': {
            'title': 'titititle',
            'content': 'connn',
            # empty list?
            'image': None
        },
        'form': [
            {
                'sign': 1,
                'name': 'form1',
                'bg_color': '#c4f0dd',
                'tx_color': '#313131'
            }
        ],
        'field': [
            {
                'sign': 1,
                # why became string?
                'type': '1',
                'name': 'text',
                'holder': 'text',
                'form_group_id': 1,
                'back_color': '#287BFF',
                'text_color': '#fafafa',
                'list': [],
                'image_data': []
            }
        ],
        'order': [
            {
                'sign': 1,
                'type': 1,
                'name': 'new layout',
                'position': {
                    'x': 230,
                    'y': 50,
                    'w': 455,
                    'h': 345,
                    'z': 1
                },
                'image_data': [],
                # image url null filter??
                'image_url': '',
                'video_type': 1
            }
        ]
    }
}
