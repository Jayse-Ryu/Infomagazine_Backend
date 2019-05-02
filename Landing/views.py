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


class LandingViewSet(ViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):

    def create(self, request):

        req = json.loads(request.body)

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        # s3 = session.resource('s3')
        # s3.upload_file('filename.file', 'rewrite-streaming-dev', 'savename.file')

        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = table.put_item(
            Item={
                "CompanyNum": req['CompanyNum'],
                "LandingNum": req['LandingNum'],
                "LandingInfo": req['LandingInfo'],
                "UpdatedTime": req['UpdatedTime']
            }
        )

        if dynamo_db_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return Response(req, status=status.HTTP_200_OK)
        else:
            return Response(req, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        print('Get function activated')

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
        print('Retrieve function activated')

        sign_param = str(json.loads(kwargs['pk']))
        # print(sign_param)

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = \
            table.query(
                IndexName='LandingNum-index',
                KeyConditionExpression=Key('LandingNum').eq(sign_param),
                ScanIndexForward=False
            )

        dynamo_obj = dynamo_db_res['Items'][0]

        print('ret by obj', dynamo_obj['LandingInfo']['landing']['name'])

        get_manger = self.get_manager(dynamo_obj['LandingInfo']['landing']['manager'])
        get_company = self.get_company(dynamo_obj['LandingInfo']['landing']['company'])
        collection_amount = len(dynamo_obj['LandingInfo']['landing']['collections'])
        dynamo_obj['LandingInfo']['landing']['manager_name'] = get_manger
        dynamo_obj['LandingInfo']['landing']['company_name'] = get_company
        dynamo_obj['LandingInfo']['landing']['collection_amount'] = collection_amount

        preview = self.request.query_params.get('preview', None)
        if preview is not None:
            self.create_html(json.loads(json.dumps(dynamo_obj, cls=DecimalEncoder)))
            return Response(status=status.HTTP_200_OK)

        return Response(dynamo_obj, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        print('List function activated')

        manager_queryset = UserAccess.objects.all()
        manager_serializer_class = UserAccessSerializer
        company_queryset = Company.objects.all()
        company_serializer_class = CompanySerializer

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2',
        )

        # Dynamo filter start
        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        # Get params from url
        # Authorization
        auth = self.request.query_params.get('auth', None)
        auth_code = self.request.query_params.get('auth_code', None)
        main = self.request.query_params.get('main', None)

        # Search params
        manager = self.request.query_params.get('manager', None)
        company = self.request.query_params.get('company', None)
        name = self.request.query_params.get('name', None)

        # List for serializer
        init_company = []
        manager_filter = []
        company_filter = []
        dynamo_obj = []

        # Get list of manager or company as params
        if manager is not None:
            manager_queryset = manager_queryset.filter(
                Q(user__full_name__icontains=manager) | Q(user__account__icontains=manager)
            )
            manager_serializer = manager_serializer_class(manager_queryset, many=True)
            for results in manager_serializer.data:
                manager_filter.append(int(json.dumps(results['user'])))

        if company is not None:
            company_queryset = company_queryset.filter(
                Q(name__icontains=company) | Q(sub_name__icontains=company)
            )
            company_serializer = company_serializer_class(company_queryset, many=True)
            for results in company_serializer.data:
                company_filter.append(int(json.dumps(results['id'])))

        if auth is not None:
            if auth in 'staff':
                # Filtering Company as manager's organization
                init_company_qs = Company.objects.all()
                init_company_serializer = company_serializer_class(init_company_qs, many=True)

                for results in init_company_serializer.data:
                    init_company.append(int(json.dumps(results['id'])))

                # Get Search parameters
                if manager is not None:
                    # Manager search(manager) in all of companies(init_company)
                    if len(manager_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.manager').is_in(manager_filter),
                                    ScanIndexForward=False
                                )
                            if len(dynamo_db_res['Items']) is not 0:
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)

                elif company is not None:
                    # Company search(company) in all of company(init_company)
                    if len(company_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.company').is_in(company_filter),
                                    ScanIndexForward=False
                                )

                            if len(dynamo_db_res['Items']) is not 0:
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)
                            # else none

                elif name is not None:
                    # Landing name search in all of company(init_company)
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                FilterExpression=Attr('LandingInfo.landing.name').contains(name),
                                ScanIndexForward=False
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

                elif main is not None:
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                FilterExpression=Attr('LandingInfo.landing.base_url').eq(main),
                                ScanIndexForward=True
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

                else:
                    print('staff has no search param')
                    # When search parameters not existed, get all of list
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                ScanIndexForward=True
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

            elif auth in 'manager':
                # Filtering Company as manager's organization
                init_company_qs = Company.objects.all()
                init_company_qs = init_company_qs.filter(organization__exact=auth_code)
                init_company_serializer = company_serializer_class(init_company_qs, many=True)

                for results in init_company_serializer.data:
                    init_company.append(int(json.dumps(results['id'])))

                # Get Search parameters
                if manager is not None:
                    # Manager search(manager) in only my organization's company(init_company)
                    if len(manager_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.manager').is_in(manager_filter),
                                    ScanIndexForward=False
                                )
                            if len(dynamo_db_res['Items']) is not 0:
                                # dynamo_obj.append(dynamo_db_res['Items'][0])
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)

                elif company is not None:
                    # Company search(company) in only my organization's company(init_company)
                    if len(company_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.company').is_in(company_filter),
                                    ScanIndexForward=False
                                )

                            if len(dynamo_db_res['Items']) is not 0:
                                # dynamo_obj.append(dynamo_db_res['Items'][0])
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)
                            # else none

                elif name is not None:
                    # Landing name search in only my organization's company(init_company)
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                FilterExpression=Attr('LandingInfo.landing.name').contains(name),
                                ScanIndexForward=False
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            # dynamo_obj.append(dynamo_db_res['Items'][0])
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

                else:
                    # When search parameters not existed, get all of list from init company
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                ScanIndexForward=False
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            # dynamo_obj.append(dynamo_db_res['Items'][0])
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

            elif auth in 'customer':
                # Limit Company as customer's company
                init_company.append(auth_code)

                if manager is not None:
                    # Manager search(manager) in only my organization's company(init_company)
                    if len(manager_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.manager').is_in(manager_filter),
                                    ScanIndexForward=False
                                )
                            if len(dynamo_db_res['Items']) is not 0:
                                # dynamo_obj.append(dynamo_db_res['Items'][0])
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)

                elif company is not None:
                    # Company search(company) in only my company(init_company)? it looks useless
                    if len(company_filter) is not 0:
                        for item_company in init_company:
                            dynamo_db_res = \
                                table.query(
                                    IndexName='CompanyNum-UpdatedTime-index',
                                    KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                    FilterExpression=Attr('LandingInfo.landing.company').is_in(company_filter),
                                    ScanIndexForward=False
                                )

                            if len(dynamo_db_res['Items']) is not 0:
                                # dynamo_obj.append(dynamo_db_res['Items'][0])
                                for items in dynamo_db_res['Items']:
                                    dynamo_obj.append(items)
                            # else none

                elif name is not None:
                    # Landing name search in only my company(init_company)
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                FilterExpression=Attr('LandingInfo.landing.name').contains(name),
                                ScanIndexForward=False
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            # dynamo_obj.append(dynamo_db_res['Items'][0])
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

                else:
                    # When search parameters not existed, get all of list from my company
                    for item_company in init_company:
                        dynamo_db_res = \
                            table.query(
                                IndexName='CompanyNum-UpdatedTime-index',
                                KeyConditionExpression=Key('CompanyNum').eq(str(item_company)),
                                ScanIndexForward=False
                            )
                        if len(dynamo_db_res['Items']) is not 0:
                            # dynamo_obj.append(dynamo_db_res['Items'][0])
                            for items in dynamo_db_res['Items']:
                                dynamo_obj.append(items)

            elif auth in 'none':
                print('auth none?', auth)
                print('code?', auth_code)
                # return none

        # Add company name and manager name in list
        final_result = []
        for tem in dynamo_obj:
            if tem['LandingInfo']['landing']['name'] is not None:
                get_manger = self.get_manager(tem['LandingInfo']['landing']['manager'])
                get_company = self.get_company(tem['LandingInfo']['landing']['company'])
                collection_amount = len(tem['LandingInfo']['landing']['collections'])
                tem['LandingInfo']['landing']['manager_name'] = get_manger
                tem['LandingInfo']['landing']['company_name'] = get_company
                tem['LandingInfo']['landing']['collection_amount'] = collection_amount
                final_result.append(tem)

        # self.bubble_sort(dynamo_obj)
        self.bubble_sort(final_result)

        return Response(final_result, status=status.HTTP_200_OK)

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

    def bubble_sort(self, list):
            def swap(i, j):
                list[i], list[j] = list[j], list[i]

            n = len(list)
            swapped = True

            x = -1
            while swapped:
                swapped = False
                x = x + 1
                for i in range(1, n - x):
                    if list[i - 1]['LandingNum'] < list[i]['LandingNum']:
                        swap(i - 1, i)
                        swapped = True
            return list

    def destroy(self, request, *args, **kwargs):
        print('Destroy function activated')
        sign_param = str(json.loads(kwargs['pk']))

        item_obj = []

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        dynamo_db = session.resource('dynamodb')
        table = dynamo_db.Table('Infomagazine')

        dynamo_db_res = \
            table.query(
                IndexName='LandingNum-index',
                KeyConditionExpression=Key('LandingNum').eq(sign_param),
                ScanIndexForward=False
            )

        if len(dynamo_db_res['Items']) is not 0:
            item_obj.append(dynamo_db_res['Items'][0])

        company_num = item_obj[0]['CompanyNum']

        if company_num is not 0 and company_num is not None:
            table.delete_item(
                Key={
                    'CompanyNum': company_num,
                    'LandingNum': sign_param
                }
            )
            return Response(status=status.HTTP_200_OK)
        else:
            print('Fail to get company number')
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create_html(self, landing):
        print('updated time?', landing['LandingInfo']['landing'])
        landing_info = landing['LandingInfo']['landing']

        if landing_info['title'] is not None:
            title = (landing_info['title'])
        else:
            title = '페이지'

        print('final title is = ', title)

        contents = f'''
        <!DOCTYPE html>
        <html lang="en">
        
        <head>
          <meta charset="UTF-8">
          <title>{title}</title>
        '''

        print('print contents', contents)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
