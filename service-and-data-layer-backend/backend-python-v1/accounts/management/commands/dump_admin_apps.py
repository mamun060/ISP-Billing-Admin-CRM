from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Dump admin app list for first superuser"

    def handle(self, *args, **options):
        User = get_user_model()
        su = User.objects.filter(is_superuser=True).first()
        if not su:
            self.stdout.write("No superuser found")
            return

        rf = RequestFactory()
        request = rf.get('/admin/')
        request.user = su

        site = admin.site
        import importlib
        from django.conf import settings
        from django.contrib.admin import sites as admin_sites

        self.stdout.write(f"admin.site: {site!r} (module={site.__class__.__module__})")
        self.stdout.write(f"django.contrib.admin.sites.site: {admin_sites.site!r} (module={admin_sites.site.__class__.__module__})")
        try:
            import django.contrib.admin.decorators as dec
            self.stdout.write(f"decorators.default_site: {dec.default_site!r} (module={dec.default_site.__class__.__module__})")
        except Exception as e:
            self.stdout.write(f"couldn't read decorators.default_site: {e}")

        # Try importing each app's admin module to catch import-time errors
        for app in settings.INSTALLED_APPS:
            try:
                modname = f"{app}.admin"
                importlib.import_module(modname)
                self.stdout.write(f"imported {modname} (registry={len(site._registry)})")
            except Exception as e:
                self.stdout.write(f"import {app}.admin failed: {e} (registry={len(site._registry)})")

        # Run autodiscover as well (may be redundant)
        try:
            from django.contrib import admin as admin_pkg

            admin_pkg.autodiscover()
        except Exception as e:
            self.stdout.write(f"autodiscover error: {e}")

        app_list = site.get_app_list(request)
        self.stdout.write(f"Apps visible: {len(app_list)}")
        for app in app_list:
            self.stdout.write(f"- {app.get('name')} ({app.get('app_label')}) -> {len(app.get('models', []))} models")
        # Also print whether user passes has_permission
        has_perm = site.has_permission(request)
        self.stdout.write(f"site.has_permission: {has_perm}")
        self.stdout.write(f"Registered models: {len(site._registry)}")
        for model, model_admin in site._registry.items():
            try:
                name = f"{model._meta.app_label}.{model._meta.model_name}"
            except Exception:
                name = str(model)
            has_module = model_admin.has_module_permission(request)
            has_view = model_admin.has_view_permission(request)
            self.stdout.write(f"- {name}: has_module={has_module}, has_view={has_view}")
        # Print all AdminSite instances tracked
        try:
            from django.contrib.admin.sites import all_sites
            for s in all_sites:
                self.stdout.write(f"all_sites member: {s!r} module={s.__class__.__module__} registry={len(s._registry)}")
        except Exception:
            pass
