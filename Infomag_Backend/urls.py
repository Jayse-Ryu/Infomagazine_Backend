from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token  # , verify_jwt_token
from rest_framework import routers
# from rest_framework.authtoken import views

from Users.views import UserViewSet
from Company.views import CompanyViewSet
from Landing.views import LandingViewSet, LayoutViewSet
from Files.views import ImageViewSet
from Video.views import VideoViewSet
from Form.views import FormGroupViewSet, FieldViewSet
from Term.views import TermViewSet
from Url.views import UrlViewSet
from Collection.views import CollectionViewSet
from Order.views import OrderViewSet
from Organization.views import OrganizationViewSet
from UserAccess.views import UserAccessViewSet

router = routers.DefaultRouter()
# router.register('user', UserViewSet)
router.register('user', UserViewSet, base_name='user')
router.register('user_access', UserAccessViewSet, base_name='user_access')
router.register('company', CompanyViewSet, base_name='company')
router.register('organization', OrganizationViewSet, base_name='organization')
router.register('landing', LandingViewSet, base_name='landing')
router.register('layout', LayoutViewSet, base_name='layout')
router.register('order', OrderViewSet, base_name='order')
router.register('image', ImageViewSet)
router.register('video', VideoViewSet)
router.register('form_group', FormGroupViewSet, base_name='form_group')
router.register('field', FieldViewSet, base_name='field')
router.register('term', TermViewSet, base_name='term')
router.register('url', UrlViewSet, base_name='url')
router.register('collection', CollectionViewSet, base_name='collection')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    # JWT auth
    # path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-token-auth/', obtain_jwt_token),
    # path('api-token-verify', verify_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]
