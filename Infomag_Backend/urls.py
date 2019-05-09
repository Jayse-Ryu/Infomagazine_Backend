from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import routers

from Users.views import UserViewSet
from Company.views import CompanyViewSet
from Organization.views import OrganizationViewSet
from UserAccess.views import UserAccessViewSet
from Landing.views import PreviewViewSet

router = routers.DefaultRouter()
router.register('user', UserViewSet, base_name='user')
router.register('user_access', UserAccessViewSet, base_name='user_access')
router.register('company', CompanyViewSet, base_name='company')
router.register('organization', OrganizationViewSet, base_name='organization')
router.register('preview', PreviewViewSet, base_name='preview')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('landing/', include('Landing.urls')),

    # JWT auth
    # path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-token-auth/', obtain_jwt_token),
    # path('api-token-verify', verify_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]
