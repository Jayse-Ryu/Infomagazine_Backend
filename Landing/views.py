import os
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
        get_company = self.get_company(dynamo_obj['LandingInfo']['landing']['company'])['name']
        collection_amount = len(dynamo_obj['LandingInfo']['landing']['collections'])
        dynamo_obj['LandingInfo']['landing']['manager_name'] = get_manger
        dynamo_obj['LandingInfo']['landing']['company_name'] = get_company
        dynamo_obj['LandingInfo']['landing']['collection_amount'] = collection_amount

        # preview = self.request.query_params.get('preview', None)
        # if preview is not None:
        #     self.create_html(json.loads(json.dumps(dynamo_obj, cls=DecimalEncoder)))
        #     return Response(status=status.HTTP_200_OK)

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
                get_company = self.get_company(tem['LandingInfo']['landing']['company'])['name']
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
            return item

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


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class PreviewViewSet(ViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):

    def create(self, request, *args, **kwargs):
        print('preview create request ', request)
        print('args', args, kwargs)
        req = json.loads(request.body)

        self.create_html(req)

        return Response(status=status.HTTP_200_OK)

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
        get_company = self.get_company(dynamo_obj['LandingInfo']['landing']['company'])['name']
        collection_amount = len(dynamo_obj['LandingInfo']['landing']['collections'])
        dynamo_obj['LandingInfo']['landing']['manager_name'] = get_manger
        dynamo_obj['LandingInfo']['landing']['company_name'] = get_company
        dynamo_obj['LandingInfo']['landing']['collection_amount'] = collection_amount

        preview = self.request.query_params.get('preview', None)
        if preview is not None:
            self.create_html(json.loads(json.dumps(dynamo_obj, cls=DecimalEncoder)))
            return Response(status=status.HTTP_200_OK)

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
            return item

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

    def create_html(self, landing):
        company_num = landing['CompanyNum']
        landing_num = landing['LandingNum']
        landing_info = landing['LandingInfo']['landing']
        landing_term = landing['LandingInfo']['term']
        landing_form = landing['LandingInfo']['form']
        landing_field = landing['LandingInfo']['field']
        landing_order = landing['LandingInfo']['order']
        order_lowest = 0

        temp = {
            'manager': 4,
            'manager_name': 'Manager2',
            'company': 4,
            'company_name': 'up2 customer',
            # 'show_company': False,
            # 'name': 'mana2lan',
            # 'title': None,

            'base_url': 'main',

            # 'header_script': None,
            # 'body_script': None,

            'inner_db': True,

            # 'is_hijack': False,
            # 'hijack_url': None,

            'is_banner': False,
            'banner_url': None,
            'banner_image': None,

            'is_term': False,
            'image_term': False,

            'collections': [],
            'collection_amount': 0,

            'views': 0,
            # 'is_active': True,
            # 'is_mobile': False,

            # 'font': -1
        }

        # ## Page Title
        if landing_info['title'] is not None:
            title = (landing_info['title'])
        else:
            title = '페이지'

        # ## Landing activated
        if landing_info['is_active'] is True:
            is_active = ''
        else:
            is_active = '''
                    // This landing is not Active
                    location.replace('https://www.google.com/')
                '''

        # ## Page mobile filter in head script
        if landing_info['is_mobile'] is True:
            is_mobile = '''
                // Mobile only
                if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                    // document.addEventListener("DOMContentLoaded", function(event) { }
                    alert('is Mobile!')
                } else {
                    alert('is not Mobile')
                    location.replace('https://www.google.com/')
                }
                '''
        else:
            is_mobile = ''

        # ## Hijack function
        if landing_info['is_hijack'] is True:
            if landing_info['hijack_url'] is not None:
                hijack = '''
                    history.replaceState(null, document.title, location.pathname+"#!/stealingyourhistory");
                    history.pushState(null, document.title, location.pathname);

                    window.addEventListener("popstate", function() {
                        if(location.hash === "#!/stealingyourhistory") {
                            history.replaceState(null, document.title, location.pathname);
                            setTimeout(function(){
                                location.replace("''' + landing_info['hijack_url'] + ''''");
                            },0);
                        }
                    }, false);
                    '''
            else:
                hijack = ''
        else:
            hijack = ''

        # ## Header script
        if landing_info['header_script'] is not None:
            header_script = landing_info['header_script']
        else:
            header_script = ''

        # ## Body script
        if landing_info['body_script'] is not None:
            body_script = landing_info['body_script']
        else:
            body_script = ''

        # ## Landing Font
        if int(landing_info['font']) is 1:
            font_link = ''
            font_name = 'sans-serif'
        elif int(landing_info['font']) is 2:
            font_link = '@import url(http://fonts.googleapis.com/earlyaccess/nanumgothic.css);'
            font_name = 'Nanum Gothic'
        elif int(landing_info['font']) is 3:
            font_link = '@import url(http://fonts.googleapis.com/earlyaccess/nanummyeongjo.css);'
            font_name = 'Nanum Myeongjo'
        elif int(landing_info['font']) is 4:
            font_link = '@import url(http://fonts.googleapis.com/earlyaccess/jejugothic.css);'
            font_name = 'Jeju Gothic'
        else:
            font_link = ''
            font_name = 'serif'

        # ## Order objects
        if len(landing_order) is not 0:
            order_obj = ''
            for order in landing_order:
                # Get end of layout position for auto footer
                if order['position']['y'] + order['position']['h'] > order_lowest:
                    order_lowest = order['position']['y'] + order['position']['h']

                # Order is image
                if order['type'] is 1:
                    # order['image_url'], order['image_data']
                    order_obj += f'''
                            <section id="section_{order['sign']}" 
                                     style="margin-top: {order['position']['y'] / 10}%; 
                                     left: {order['position']['x'] / 10}%; 
                                     width: {order['position']['w'] / 10}%; 
                                     padding-bottom: {order['position']['h'] / 10}%;
                                     z-index: {order['position']['z']};">'''

                    order_obj += '''
                            <figure>
                              <img 
                                src="https://s3.ap-northeast-2.amazonaws.com/lcventures-image-cdn/images/home_main.jpg" 
                                alt="Top_bg_big">
                            </figure>
                        '''

                    order_obj += '''
                            </section>
                        '''
                # Order is form-group
                elif order['type'] is 2:
                    # order['form_group']
                    form_exist_flag = False

                    for form in landing_form:
                        if form['sign'] is order['form_group']:
                            form_exist_flag = True
                            bg_color = {
                                'r': str(int(form['bg_color'].lstrip('#')[0:2], 16)),
                                'g': str(int(form['bg_color'].lstrip('#')[2:4], 16)),
                                'b': str(int(form['bg_color'].lstrip('#')[4:6], 16))
                            }
                            tx_color = form['tx_color'].lstrip('#')
                            opacity = int(form['opacity']) / 10
                            break

                    if form_exist_flag is True:
                        order_obj += f'''
                            <section id="section_{order['sign']}" 
                                     style="margin-top: {order['position']['y'] / 10}%; 
                                     left: {order['position']['x'] / 10}%; 
                                     width: {order['position']['w'] / 10}%; 
                                     padding-bottom: {order['position']['h'] / 10}%;
                                     z-index: {order['position']['z']};
                                     background-color: rgba({bg_color['r']},{bg_color['g']},{bg_color['b']},{opacity});
                                     color: #{tx_color};">
                                <form onsubmit = "event.preventDefault(); form_submit();">
                                    <div class="form_wrap">
                        '''
                        for field in landing_field:
                            if field['form_group_id'] is order['form_group']:
                                if field['type'] is 1:
                                    # 1 text, name, holder, label(t,f)
                                    if field['label'] is True:
                                        order_obj += f'''
                                                <div class="field_wrap box_with_label" style="width: 100%;">
                                                  <label class="field_label" for="{field['name']}{field['sign']}">
                                                      {field['name']}
                                                  </label>
                                                  <input type="text" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}"
                                                         maxlength="25">
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap box_without_label" style="width: 100%;">
                                                  <input type="text" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}"
                                                         maxlength="25">
                                                </div>
                                            '''
                                elif field['type'] is 2:
                                    # 2 num, same
                                    if field['label'] is True:
                                        order_obj += f'''
                                                <div class="field_wrap box_with_label" style="width: 100%;">
                                                  <label class="field_label" for="{field['name']}{field['sign']}">
                                                      {field['name']}
                                                  </label>
                                                  <input type="number" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}"
                                                         maxlength="25">
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap box_without_label" style="width: 100%;">
                                                  <input type="number" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}"
                                                         maxlength="25">
                                                </div>
                                            '''
                                elif field['type'] is 3:
                                    # 3 scr, list
                                    if field['label'] is True:
                                        order_obj += f'''
                                            <div class="field_wrap box_with_label" style="width: 100%;">
                                              <label class="field_label" for="{field['name']}{field['sign']}">
                                                  {field['name']}
                                              </label>
                                              <select id="{field['name']}{field['sign']}">
                                                <option value="0">{field['holder']}</option>
                                            '''
                                        for list_item in field['list']:
                                            order_obj += f'''
                                                    <option value="{list_item}">{list_item}</option>
                                                '''
                                        order_obj += f'''
                                                </select>
                                            </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                            <div class="field_wrap box_without_label" style="width: 100%;">
                                              <select id="{field['name']}{field['sign']}">
                                                <option value="0">{field['holder']}</option>
                                            '''
                                        for list_item in field['list']:
                                            order_obj += f'''
                                                    <option value="{list_item}">{list_item}</option>
                                                '''
                                        order_obj += f'''
                                                </select>
                                            </div>
                                            '''
                                elif field['type'] is 4:
                                    # 4 radio, list
                                    if field['label'] is True:
                                        order_obj += f'''
                                                <div class="field_wrap list_with_label" style="width: 100%;">
                                                  <label class="field_label">{field['name']}</label>
                                                  <div class="list_wrap">
                                            '''
                                        for index, list_item in enumerate(field['list']):
                                            order_obj += f'''
                                                    <span style="white-space: nowrap;">
                                                      <input type="radio" 
                                                             value="{list_item}" 
                                                             name="radio_{field['sign']}" 
                                                             id="{field['name']}{field['sign']}{index}">
                                                      <label class="list_label" for="{field['name']}{field[
                                                'sign']}{index}">
                                                        {list_item}
                                                      </label>
                                                    </span>
                                                '''
                                        order_obj += '''
                                                  </div>
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap list_without_label" style="width: 100%;">
                                                  <div class="list_wrap">
                                            '''
                                        for index, list_item in enumerate(field['list']):
                                            order_obj += f'''
                                                    <span style="white-space: nowrap;">
                                                      <input type="radio" 
                                                             value="{list_item}" 
                                                             name="radio_{field['sign']}" 
                                                             id="{field['name']}{field['sign']}{index}">
                                                      <label class="list_label" for="{field['name']}{field[
                                                'sign']}{index}">
                                                        {list_item}
                                                      </label>
                                                    </span>
                                                '''
                                        order_obj += '''
                                                  </div>
                                                </div>
                                            '''

                                elif field['type'] is 5:
                                    # 5 chk, list
                                    if field['label'] is True:
                                        order_obj += f'''
                                                <div class="field_wrap list_with_label" style="width: 100%;">
                                                  <label class="field_label">{field['name']}</label>
                                                  <div class="list_wrap">
                                            '''
                                        for index, list_item in enumerate(field['list']):
                                            order_obj += f'''
                                                    <span style="white-space: nowrap;">
                                                      <input type="checkbox" 
                                                             value="{list_item}" 
                                                             name="radio_{field['sign']}" 
                                                             id="{field['name']}{field['sign']}{index}">
                                                      <label class="list_label" for="{field['name']}{field[
                                                'sign']}{index}">
                                                        {list_item}
                                                      </label>
                                                    </span>
                                                '''
                                        order_obj += '''
                                                  </div>
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap list_without_label" style="width: 100%;">
                                                  <div class="list_wrap">
                                            '''
                                        for index, list_item in enumerate(field['list']):
                                            order_obj += f'''
                                                    <span style="white-space: nowrap;">
                                                      <input type="checkbox" 
                                                             value="{list_item}" 
                                                             name="radio_{field['sign']}" 
                                                             id="{field['name']}{field['sign']}{index}">
                                                      <label class="list_label" for="{field['name']}{field[
                                                'sign']}{index}">
                                                        {list_item}
                                                      </label>
                                                    </span>
                                                '''
                                        order_obj += '''
                                                  </div>
                                                </div>
                                            '''

                                elif field['type'] is 6:
                                    # 6 date, ?
                                    if field['label'] is True:
                                        order_obj += f'''
                                                <div class="field_wrap box_with_label" style="width: 100%;">
                                                  <label class="field_label" for="{field['name']}{field['sign']}">
                                                      {field['name']}
                                                  </label>
                                                  <input type="date" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}">
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap box_without_label" style="width: 100%;">
                                                  <input type="date" 
                                                         id="{field['name']}{field['sign']}" 
                                                         placeholder="{field['holder']}">
                                                </div>
                                            '''

                                elif field['type'] is 7:
                                    # 7 link, url
                                    if field['image_data'] is None:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <a href="{field['url']}" target="_blank">
                                                        <button class="form_button" 
                                                                type="button"
                                                                style="
                                                                    background-color: {field['back_color']};
                                                                    color: {field['text_color']}">
                                                            {field['holder']}
                                                        </button> 
                                                    </a>
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <a href="{field['url']}">
                                                        <button class="form_button" type="button">
                                                            {field['holder']}
                                                            <img src="" alt="{field['holder']}">
                                                        </button> 
                                                    </a>
                                                </div>
                                            '''

                                elif field['type'] is 8:
                                    # 8 tel, value
                                    if field['image_data'] is None:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <a href="tel:{field['value']}">
                                                        <button class="form_button" 
                                                                type="button"
                                                                style="
                                                                    background-color: {field['back_color']};
                                                                    color: {field['text_color']}">
                                                            {field['holder']}
                                                        </button>
                                                    </a>
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <a href="tel:{field['value']}">
                                                        <button class="form_button" type="button">
                                                            {field['holder']}
                                                            <img src="" alt="{field['holder']}">
                                                        </button> 
                                                    </a>
                                                </div>
                                            '''

                                elif field['type'] is 9:
                                    # 9 done (not done :D)
                                    if field['image_data'] is None:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <button class="form_button" 
                                                            type="submit"
                                                            style="
                                                                background-color: {field['back_color']};
                                                                color: {field['text_color']}">
                                                        {field['holder']}
                                                    </button> 
                                                </div>
                                            '''
                                    else:
                                        order_obj += f'''
                                                <div class="field_wrap button_wrap" style="width: 100%;">
                                                    <button class="form_button" type="submit">
                                                        <img src="" alt="holder">
                                                    </button> 
                                                </div>
                                            '''

                                elif field['type'] is 10:
                                    # 10 term chk
                                    order_obj += f'''
                                            <div class="field_wrap term_wrap" style="width: 100%;">
                                                <input type="checkbox" id="term{field['sign']}">
                                                <label for="term{field['sign']}">{field['holder']}</label>
                                                <span>[약관보기]</span>
                                            </div>
                                        '''

                    order_obj += '''
                                    </div>
                                    <!-- /form_wrap -->
                                </form>
                            </section>
                        '''

                # Order is video
                elif order['type'] is 3:
                    # order['video_type'], order['video_data]
                    order_obj += f'''
                            <section id="section_{order['sign']}" 
                                     style="margin-top: {order['position']['y'] / 10}%; 
                                     left: {order['position']['x'] / 10}%; 
                                     width: {order['position']['w'] / 10}%; 
                                     padding-bottom: {order['position']['h'] / 10}%;
                                     z-index: {order['position']['z']};">'''

                    if int(order['video_type']) is 1:
                        # Youtube
                        order_obj += f'''
                                <div class="video_wrap">
                                    <div style=" position: relative; padding-bottom: 56.25%; height:0;">
                                        <iframe style="width: 100%; height: 100%; top:0; left:0; position: absolute;" 
                                                type="text/html"
                                                src="https://www.youtube.com/embed/{order[
                            'video_data']}?&playlist=Ra8s0IHng6A&autoplay=0&loop=1&showinfo=0&fs=1&disablekb=1&vq=auto&controls=0&rel=0&iv_load_policy=3&mute=0&playsinline=1&modestbranding=1"
                                                frameborder="0" volume="1" allowfullscreen webkitallowfullscreen
                                                mozallowfullscreen>
                                        </iframe>
                                    </div>
                                </div>
                            '''
                    elif int(order['video_type']) is 2:
                        # Vimeo
                        order_obj += f'''
                                <div class="video_wrap">
                                    <div style=" position: relative; padding-bottom: 56.25%; height:0;">
                                        <iframe style="width: 100%; height: 100%; top:0; left:0; position: absolute;" 
                                                type="text/html"
                                                src="https://player.vimeo.com/video/{order['video_data']}?&loop=1" 
                                                frameborder="0" volume="1" 
                                                webkitallowfullscreen mozallowfullscreen allowfullscreen>
                                        </iframe>
                                    </div>
                                </div>
                            '''

                    order_obj += '''
                            </section>
                        '''
        else:
            print('There is no order in this landing', landing_order)

        if landing_info['show_company'] is True:
            company_obj = json.loads(json.dumps(self.get_company(landing_info['company'])))

            # Footer position below lowest order layout
            if order_lowest is 0:
                footer = '''
                        <footer style="margin-top: 0;">
                    '''
            else:
                footer = f'''
                        <footer style="margin-top: {order_lowest / 10}%;">
                            <p class="footer_content">
                    '''

            # Get company footer items and spread
            footer_in = []
            if company_obj['sub_name'] is not None:
                footer_in.append(f"<span>{company_obj['sub_name']}</span>")
            elif company_obj['name'] is not None:
                footer_in.append(f"<span>{company_obj['name']}</span>")

            if company_obj['header'] is not None:
                footer_in.append(f"<span>{company_obj['header']}</span>")

            if company_obj['phone'] is not None:
                footer_in.append(f'''<a href="tel:{company_obj['phone']}"><span>{company_obj['phone']}</span></a>''')

            if company_obj['email'] is not None:
                footer_in.append(f'''<a href="mailto:{company_obj['email']}"><span>{company_obj['email']}</span></a>''')

            if company_obj['corp_num']:
                footer_in.append(f'''<span>{company_obj['corp_num']}</span>''')

            if company_obj['address'] is not None:
                footer_in.append(f'''<span>{company_obj['address']}</span>''')

            # Spread
            for index, item in enumerate(footer_in):
                footer += item
                if index < len(footer_in) - 1:
                    footer += ' | '

            footer += '''
                    </footer>
                '''
        else:
            footer = ''

        # ## Header CSS with font import
        style_sheet = '''
              <style type="text/css">
              '''
        style_sheet += f'''
                {font_link}
            '''
        style_sheet += '''
                /* @media (min-width: 576px) {  }

                @media (min-width: 768px) {  }

                @media (min-width: 992px) {  }

                @media (min-width: 1200px) {  }*/

                /* Main */
                * {
                  -webkit-box-sizing: border-box;
                  -moz-box-sizing: border-box;
                  box-sizing: border-box;'''
        style_sheet += f'''
                  font-family: '{font_name}', serif; 
            '''
        style_sheet += '''
                }
                body {
                  padding: 0;
                  margin: 0;
                  font-size: 1.2em;
                }
                main {
                  position: absolute;
                  width: 100%;
                }

                a {
                  background-color: transparent;
                  text-decoration: none !important;
                  color: unset;
                }

                a:active,
                a:hover {
                  outline: 0 !important;
                }

                /* /Main */

                /* Responsive Wrap */
                .overall_wrap {
                  position: relative;
                  width: 100%;
                  min-width: 360px;
                  margin: 0 auto;
                }

                @media (max-width: 768px) {
                  * {
                    font-size: 0.9em;
                  }
                }
                @media (min-width: 768px) and (max-width: 1000px) {
                  * {
                    font-size: 1em;
                  }
                }
                @media (min-width: 1001px) {
                  .overall_wrap {
                    max-width: 1000px;
                  }
                }
                /* /Responsive Wrap */


                /* Layout Initial */
                section, footer {
                  position: absolute;
                  width: 100%;
                }
                section form {
                  position: absolute;
                  width: 100%;
                  height: 100%;
                  overflow: auto;
                }

                footer {
                  padding: 3%;
                  text-align: center;
                  font-size: 0.9em;
                  background-color: #f5f5f5;
                }

                footer p span {
                  word-break: keep-all;
                  white-space: nowrap;
                }

                .form_wrap {
                  position: absolute;
                  width: 100%;
                  padding: 3%;
                  top: 50%;
                  -webkit-transform: translateY(-50%);
                  -moz-transform: translateY(-50%);
                  -ms-transform: translateY(-50%);
                  -o-transform: translateY(-50%);
                  transform: translateY(-50%);
                }

                @media (max-width: 1000px) {
                  .form_wrap {
                    top: 0;
                    -webkit-transform: none;
                    -moz-transform: none;
                    -ms-transform: none;
                    -o-transform: none;
                    transform: none;
                  }
                }

                form input, form select {
                  position: relative;
                  display: inline-block;
                  height: calc(2.25rem + 2px);
                  padding: .375rem .75rem;
                  font-size: 1em;
                  vertical-align: middle;
                  line-height: 1.5;
                  color: #495057;
                  background-color: #fff;
                  border: 1px solid #ced4da;
                  border-radius: .25rem;
                }
                input[type=radio], input[type=checkbox] {
                  height: calc(1.9rem + 2px);
                }
                form label {
                  vertical-align: top;
                  text-align: center;
                  margin-top: 0.5rem;
                  padding-top: calc(.25rem - 2px);
                  padding-bottom: calc(.25rem + 1px);
                  font-size: .875rem;
                  line-height: 1.5;
                }
                figure {
                  position: absolute;
                  width: 100%;
                  height: 100%;
                  margin: 0;
                  text-align: center;
                }
                figure img {
                  max-width: 100%;
                  max-height: 100%;
                }
                /* /Layout Initial */

                .field_wrap {
                  display: inline-block;
                  margin: 0.5rem 0;
                }

                .box_with_label .field_label {
                  display: inline-block;
                  width: calc(25% - 10px);
                }
                .box_with_label input, .box_with_label select {
                  width: 75%;
                }

                .box_without_label .field_label {
                  display: none;
                }
                .box_without_label input, .box_without_label select {
                  width: 100%;
                }

                .list_with_label .field_label {
                  display: inline-block;
                  width: calc(25% - 10px);
                }

                .list_with_label .list_wrap{
                  display: inline-block;
                  width: 75%;
                  padding-top: calc(.25rem - 2px);
                  padding-bottom: calc(.25rem + 1px);
                }

                .list_without_label .field_label {
                  display: none;
                }

                .list_without_label .list_wrap{
                  display: inline-block;
                  width: 100%;
                  padding-top: calc(.25rem - 2px);
                  padding-bottom: calc(.25rem + 1px);
                }

                .list_label {
                  vertical-align: middle;
                }

                @media (max-width: 768px) {
                  .field_wrap {
                    width: 100% !important;
                  }

                  .box_with_label label {
                    width: 100%;
                    display: inline-block;
                    margin-bottom: 0.5rem;
                    text-align: left;
                  }
                  .box_with_label input, .box_with_label select {
                    width: 100%;
                  }

                  .list_with_label .field_label {
                    width: 100%;
                    display: inline-block;
                    margin-bottom: 0.5rem;
                    text-align: left;
                  }

                  .list_with_label .list_wrap {
                    width: 100%;
                  }
                }

                .form_button {
                    width: 100%;
                    display: inline-block;
                    font-weight: 400;
                    text-align: center;
                    white-space: nowrap;
                    vertical-align: middle;
                    -webkit-user-select: none;
                    -moz-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                    border: 1px solid transparent;
                    padding: .375rem .75rem;
                    font-size: 1rem;
                    line-height: 1.5;
                    cursor: pointer;
                    border-radius: .25rem;
                    transition: opacity .15s ease-in-out;
                }

                .form_button:hover {
                    opacity: 0.7;
                }

                .video_wrap {
                  position: absolute;
                  width: 100%;
                  top: 50%;
                  left: 0;
                  transform: translateY(-50%);
                }

              </style>
            '''

        form_submit = '''
                function form_submit() {
                    console.log('test');
                }
            '''

        # ## Render HTML file
        contents = f'''
                <!DOCTYPE html>
                <html lang="en">

                <head>
                  <meta charset="UTF-8">
                  <title>{title}</title>
                  <script>
                    {is_active}
                    {is_mobile}
                    {header_script}
                  </script>
                  {style_sheet}
                </head>
                <body>
                    <main>
                        <div class="overall_wrap">
                            {order_obj}

                            {footer}
                        </div> <!-- /div overall wrap -->
                    </main>

                    <!-- Body script -->
                    <script>
                        {hijack}
                        {body_script}
                        {form_submit}
                    </script>
                    <!-- /Body script -->
                </body>
                </html>
            '''

        preview_html = open('./temp.html', 'w')
        preview_html.write(contents)
        preview_html.close()

        session = boto3.session.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            # aws_session_token=config('AWS_SESSION_TOKEN'),
            region_name='ap-northeast-2'
        )

        s3 = boto3.client(
            's3',
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
            region_name='ap-northeast-2'
        )

        # s3 = session.resource('s3')
        # s3 = boto3.client('s3')
        s3.upload_file('./temp.html', 'lcventures-web', f'''preview_{landing_num}.html''')
