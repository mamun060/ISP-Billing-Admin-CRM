from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import FormDefinition
from .services import resolve_field_access


class FormSchemaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, form_key: str):
        try:
            form = FormDefinition.objects.get(code=form_key)
        except FormDefinition.DoesNotExist:
            return Response({"detail": "form not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        roles = []
        if user and hasattr(user, "roles"):
            roles = [ur.role for ur in user.roles]

        fields = []
        for f in form.fields.all():
            access = resolve_field_access(roles, form, f.key)
            fields.append({
                "key": f.key,
                "label": f.name,
                "input_type": f.field_type or "text",
                "access_level": access,
            })

        return Response({"form": form.code, "fields": fields})
