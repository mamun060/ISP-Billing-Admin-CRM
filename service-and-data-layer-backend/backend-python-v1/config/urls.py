from django.contrib import admin
from django.urls import include, path

# Ensure models registered to the default AdminSite are available on Unfold's
# AdminSite. Some admin registrations may have happened against the original
# django.contrib.admin.sites.site instance; copy those into the active
# `admin.site` (UnfoldAdminSite) so the sidebar shows them.
try:
    from django.contrib import admin as django_admin_pkg
    from django.contrib.admin import sites as admin_sites

    default_site = admin_sites.site
    active_site = admin.site

    # If registrations ended up on a different AdminSite instance (common when
    # the admin app was imported before DEFAULT_ADMIN_SITE took effect), copy
    # any models from those sites into the active Unfold admin site so they
    # appear in the sidebar.
    try:
        from django.contrib.admin.sites import all_sites

        for s in list(all_sites):
            if s is active_site:
                continue
            # copy only if the other site has registrations
            if getattr(s, '_registry', None):
                for model, model_admin in list(s._registry.items()):
                    if model not in active_site._registry:
                        active_site._registry[model] = model_admin
    except Exception:
        # ignore any issues enumerating sites
        pass
except Exception:
    # best-effort; if something goes wrong, don't break URL configuration
    pass
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path("api/packages/", include("packages.urls")),
    path("api/form-permissions/", include("form_permissions.urls")),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


# site branding
admin.site.site_header = "ISP Billing CRM Admin"
admin.site.site_title = "ISP Billing CRM"
admin.site.index_title = "Administration"