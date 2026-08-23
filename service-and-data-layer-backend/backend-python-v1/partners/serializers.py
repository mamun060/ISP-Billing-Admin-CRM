from rest_framework import serializers

from .models import Division, District, Upazila, Union, Partner
from .models import CommissionAgreement
from django.utils import timezone


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ["id", "name", "code"]


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name", "division_id", "code"]


class UpazilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upazila
        fields = ["id", "name", "district_id", "code"]


class UnionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Union
        fields = ["id", "name", "upazila_id", "code"]


class PartnerSerializer(serializers.ModelSerializer):
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, write_only=True)

    class Meta:
        model = Partner
        fields = ["id", "name", "code", "type", "parent_id", "commission_rate"]

    def create(self, validated_data):
        commission_rate = validated_data.pop("commission_rate", None)
        partner = super().create(validated_data)
        if commission_rate is not None:
            parent_partner = partner.parent if partner.parent_id else None
            CommissionAgreement.objects.create(
                partner=partner,
                parent=parent_partner,
                pool_percentage=commission_rate,
                effective_from=timezone.localdate(),
            )
        return partner
