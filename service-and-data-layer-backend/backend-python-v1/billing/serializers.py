from rest_framework import serializers

from .models import Client
from form_permissions.serializers import DynamicFieldsModelSerializer


class ClientSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "phone", "national_id", "email", "address", "division_id", "district_id", "upazila_id", "union_id"]
