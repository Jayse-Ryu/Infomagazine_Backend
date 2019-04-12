from django.urls import path, include
from rest_framework import routers

from .views import LandingViewSet

router = routers.DefaultRouter()
router.register('', LandingViewSet, base_name='landing')

urlpatterns = [
    path('api/', include(router.urls))
]
