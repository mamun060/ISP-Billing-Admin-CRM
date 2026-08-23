from rest_framework import permissions, viewsets

from accounts.permissions import HasModulePermission
from .models import Package
from .serializers import PackageSerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [HasModulePermission(permission_code="package.manage")]
        return [permission() for permission in permission_classes]
