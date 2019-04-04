# from rest_framework import viewsets
# from .models import Video
# from .serializers import VideoSerializer
# import boto3
#
#
# class VideoViewSet(viewsets.ModelViewSet):
#     queryset = Video.objects.all()
#     serializer_class = VideoSerializer
#
#     def create(self, request, *args, **kwargs):
#         print('self', self)
#         print('request data', request.data)
#         print('request param', request.query_params)
#         print('*arg', args)
#         print('**kwargs', kwargs)
#
#         dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2', endpoint_url="http://localhost:8000")
#         table = dynamodb.Table('infomagazine')
#
#         print("Table status:", table.table_status)
#         table = dynamodb.Table('infomagazine')
#
#         table.put_item(
#             # Item=request.data
#             Item={
#                 'LandingNum': 1
#             }
#         )
#
#         print('table status', table.table_status)
