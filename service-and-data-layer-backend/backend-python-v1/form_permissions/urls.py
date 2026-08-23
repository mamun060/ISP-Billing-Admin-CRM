from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_template import AccessTemplateViewSet
from .views_schema import FormSchemaView

router = DefaultRouter()
router.register(r"templates", AccessTemplateViewSet, basename="accesstemplate")

urlpatterns = [
    path("", include(router.urls)),
    path("forms/<str:form_key>/schema/", FormSchemaView.as_view(), name="form-schema"),
]
