from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_template import AccessTemplateViewSet

router = DefaultRouter()
router.register(r"templates", AccessTemplateViewSet, basename="accesstemplate")

urlpatterns = [
    path("", include(router.urls)),
]
