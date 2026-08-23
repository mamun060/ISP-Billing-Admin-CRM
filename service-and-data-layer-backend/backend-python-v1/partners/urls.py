from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DivisionListView,
    DistrictListView,
    UpazilaListView,
    UnionListView,
    PartnerViewSet,
)

router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partner")

urlpatterns = [
    path("", include(router.urls)),
    path("divisions/", DivisionListView.as_view(), name="divisions-list"),
    path("districts/", DistrictListView.as_view(), name="districts-list"),
    path("upazilas/", UpazilaListView.as_view(), name="upazilas-list"),
    path("unions/", UnionListView.as_view(), name="unions-list"),
]
