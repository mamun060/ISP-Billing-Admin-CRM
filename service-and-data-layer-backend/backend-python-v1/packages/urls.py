from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PackageViewSet

router = DefaultRouter()
router.register(r"", PackageViewSet, basename="package")

urlpatterns = [
    path("", include(router.urls)),
]
