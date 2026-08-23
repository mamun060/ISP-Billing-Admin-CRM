from rest_framework import serializers

from .models import Division, District, Upazila, Union, Partner, Zone, Area
from .models import CommissionAgreement
from django.utils import timezone
from form_permissions.serializers import DynamicFieldsModelSerializer


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


class ZoneSerializer(DynamicFieldsModelSerializer):
    bank_account = serializers.CharField(read_only=True)
    portal_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Zone
        fields = ["id", "name", "partner_id", "bank_account", "portal_password"]

    def create(self, validated_data):
        pwd = validated_data.pop("portal_password", None)
        bank = validated_data.pop("bank_account", None)
        zone = super().create(validated_data)
        if bank is not None:
            zone.set_bank_account(bank)
            zone.save()
        if pwd is not None:
            zone.set_portal_password(pwd)
            zone.save()
        return zone

    def update(self, instance, validated_data):
        pwd = validated_data.pop("portal_password", None)
        bank = validated_data.pop("bank_account", None)
        instance = super().update(instance, validated_data)
        if bank is not None:
            instance.set_bank_account(bank)
            instance.save()
        if pwd is not None:
            instance.set_portal_password(pwd)
            instance.save()
        return instance


class AreaSerializer(DynamicFieldsModelSerializer):
    bank_account = serializers.CharField(read_only=True)
    portal_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Area
        fields = ["id", "name", "zone_id", "bank_account", "portal_password"]

    def create(self, validated_data):
        pwd = validated_data.pop("portal_password", None)
        bank = validated_data.pop("bank_account", None)
        area = super().create(validated_data)
        if bank is not None:
            area.set_bank_account(bank)
            area.save()
        if pwd is not None:
            area.set_portal_password(pwd)
            area.save()
        return area

    def update(self, instance, validated_data):
        pwd = validated_data.pop("portal_password", None)
        bank = validated_data.pop("bank_account", None)
        instance = super().update(instance, validated_data)
        if bank is not None:
            instance.set_bank_account(bank)
            instance.save()
        if pwd is not None:
            instance.set_portal_password(pwd)
            instance.save()
        return instance
