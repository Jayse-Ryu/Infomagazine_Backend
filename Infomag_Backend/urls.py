from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token  # , verify_jwt_token
from rest_framework import routers
# from rest_framework.authtoken import views

from Users.views import UsersViewSet  # AuthorityViewSet
from Company.views import CompanyViewSet
from Landing.views import LandingViewSet
from Files.views import FilesViewSet
from Form.views import FormViewSet, LinkViewSet
from Preference.views import TermViewSet, UrlsViewSet
from Collection.views import CollectionsViewSet

router = routers.DefaultRouter()
# router.register('authority', AuthorityViewSet)
router.register('users', UsersViewSet)
router.register('company', CompanyViewSet)
router.register('landing', LandingViewSet)
router.register('files', FilesViewSet)
router.register('form', FormViewSet)
router.register('link', LinkViewSet)
router.register('term', TermViewSet)
router.register('urls', UrlsViewSet)
router.register('collections', CollectionsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    # JWT auth
    # path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api-token-auth/', obtain_jwt_token),
    # path('api-token-verify', verify_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]
