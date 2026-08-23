from rest_framework import serializers

from .models import AccessTemplate, TemplateFieldAccess
from form_permissions.models import FormDefinition, FormField


class TemplateFieldAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateFieldAccess
        fields = ["id", "form_id", "group_id", "field_id", "access"]


class AccessTemplateSerializer(serializers.ModelSerializer):
    fields = TemplateFieldAccessSerializer(many=True)

    class Meta:
        model = AccessTemplate
        fields = ["id", "name", "code", "description", "fields"]

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        template = AccessTemplate.objects.create(**validated_data)
        for f in fields_data:
            TemplateFieldAccess.objects.create(template=template, **f)
        return template

    def update(self, instance, validated_data):
        fields_data = validated_data.pop("fields", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if fields_data is not None:
            instance.fields.all().delete()
            for f in fields_data:
                TemplateFieldAccess.objects.create(template=instance, **f)
        return instance
