from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import AccessTemplate, TemplateFieldAccess
from .serializers_template import AccessTemplateSerializer
from accounts.models import Role
from .models import TemplateFieldAccess as TFA
from form_permissions.models import RoleFieldAccess


class AccessTemplateViewSet(viewsets.ModelViewSet):
    queryset = AccessTemplate.objects.all().order_by("name")
    serializer_class = AccessTemplateSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="apply-to-role")
    def apply_to_role(self, request, pk=None):
        """Apply template to a Role: creates RoleFieldAccess rows for the given role."""
        template = self.get_object()
        role_id = request.data.get("role_id")
        if not role_id:
            return Response({"detail": "role_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response({"detail": "role not found"}, status=status.HTTP_404_NOT_FOUND)

        created = []
        for tf in template.fields.all():
            # create or update RoleFieldAccess
            rfa, _ = RoleFieldAccess.objects.update_or_create(
                role=role,
                form=tf.form,
                group=tf.group,
                field=tf.field,
                defaults={"access": tf.access},
            )
            created.append(rfa.id)

        return Response({"created": created})
