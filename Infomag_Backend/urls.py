from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token  # , verify_jwt_token
from rest_framework import routers
# from rest_framework.authtoken import views

from Users.views import UserViewSet  # AuthorityViewSet
from Company.views import CompanyViewSet
from Landing.views import LandingViewSet, LayoutViewSet
from Files.views import ImageViewSet
from Form.views import FormGroupViewSet, FieldViewSet
from Preference.views import TermViewSet, UrlViewSet
from Collection.views import CollectionViewSet

router = routers.DefaultRouter()
# router.register('authority', AuthorityViewSet)
router.register('user', UserViewSet)
router.register('company', CompanyViewSet)
router.register('landing', LandingViewSet)
router.register('layout', LayoutViewSet)
router.register('image', ImageViewSet)
router.register('form_group', FormGroupViewSet)
router.register('field', FieldViewSet)
router.register('term', TermViewSet)
router.register('urls', UrlViewSet)
router.register('collection', CollectionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    # JWT auth
    # path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-token-auth/', obtain_jwt_token),
    # path('api-token-verify', verify_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]
