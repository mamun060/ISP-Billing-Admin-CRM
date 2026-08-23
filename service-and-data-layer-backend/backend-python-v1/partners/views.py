from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Division, District, Upazila, Union, Partner
from .serializers import (
    DivisionSerializer,
    DistrictSerializer,
    UpazilaSerializer,
    UnionSerializer,
    PartnerSerializer,
)


class DivisionListView(generics.ListAPIView):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [AllowAny]


class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        division_id = self.request.query_params.get("division_id")
        qs = District.objects.all()
        if division_id:
            qs = qs.filter(division_id=division_id)
        return qs


class UpazilaListView(generics.ListAPIView):
    serializer_class = UpazilaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        district_id = self.request.query_params.get("district_id")
        qs = Upazila.objects.all()
        if district_id:
            qs = qs.filter(district_id=district_id)
        return qs


class UnionListView(generics.ListAPIView):
    serializer_class = UnionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        upazila_id = self.request.query_params.get("upazila_id")
        qs = Union.objects.all()
        if upazila_id:
            qs = qs.filter(upazila_id=upazila_id)
        return qs


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # ensure CommissionAgreement is created via serializer logic
        serializer.save()
