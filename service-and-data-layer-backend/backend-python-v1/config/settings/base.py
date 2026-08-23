import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["accounts.backends.AccountsAuthBackend"]

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mptt",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "accounts",
    "partners",
    "billing",
    "commission",
    "packages",
    "form_permissions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
            "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("DB_NAME", "isp_billing_crm"),
        "USER": os.getenv("DB_USER", "mamunsfs"),
        "PASSWORD": os.getenv("DB_PASSWORD", "sfs12345"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Use Unfold's AdminSite implementation to enable Unfold context and sidebar
DEFAULT_ADMIN_SITE = "unfold.sites.UnfoldAdminSite"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//",
)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


# Unfold admin configuration
UNFOLD = {
    "SITE_TITLE": "ISP Billing CRM",
    "SITE_HEADER": "ISP Billing CRM Admin",
    "SITE_URL": "/",
    "COLORS": {
        "primary": {
            "50": "238, 242, 255",
            "100": "224, 231, 255",
            "200": "199, 210, 254",
            "300": "165, 180, 252",
            "400": "129, 140, 248",
            "500": "99, 102, 241", # Indigo-500
            "600": "79, 70, 229",
            "700": "67, 56, 202",
            "800": "55, 48, 163",
            "900": "49, 46, 129",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Overview"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Accounts"),
                "icon": "manage_accounts",
                "collapsible": True,
                "items": [
                    {"title": _("Users"), "icon": "group", "link": reverse_lazy("admin:accounts_user_changelist")},
                    {"title": _("Roles"), "icon": "admin_panel_settings", "link": reverse_lazy("admin:accounts_role_changelist")},
                    {"title": _("Permissions"), "icon": "key", "link": reverse_lazy("admin:accounts_permission_changelist")},
                    {"title": _("Role Permissions"), "icon": "key", "link": reverse_lazy("admin:accounts_rolepermission_changelist")},
                    {"title": _("User Roles"), "icon": "badge", "link": reverse_lazy("admin:accounts_userrole_changelist")},
                ],
            },
            {
                "title": _("Partners"),
                "icon": "account_tree",
                "collapsible": True,
                "items": [
                    {"title": _("Partners"), "icon": "handshake", "link": reverse_lazy("admin:partners_partner_changelist")},
                    {"title": _("Commission Agreements"), "icon": "description", "link": reverse_lazy("admin:partners_commissionagreement_changelist")},
                    {"title": _("Zones"), "icon": "map", "link": reverse_lazy("admin:partners_zone_changelist")},
                    {"title": _("Areas"), "icon": "location_city", "link": reverse_lazy("admin:partners_area_changelist")},
                    {"title": _("Divisions"), "icon": "public", "link": reverse_lazy("admin:partners_division_changelist")},
                    {"title": _("Districts"), "icon": "location_on", "link": reverse_lazy("admin:partners_district_changelist")},
                    {"title": _("Upazilas"), "icon": "location_on", "link": reverse_lazy("admin:partners_upazila_changelist")},
                    {"title": _("Unions"), "icon": "location_on", "link": reverse_lazy("admin:partners_union_changelist")},
                ],
            },
            {
                "title": _("Billing"),
                "icon": "receipt_long",
                "collapsible": True,
                "items": [
                    {"title": _("Clients"), "icon": "people", "link": reverse_lazy("admin:billing_client_changelist")},
                    {"title": _("Payment Transactions"), "icon": "payments", "link": reverse_lazy("admin:billing_paymenttransaction_changelist")},
                ],
            },
            {
                "title": _("Packages"),
                "icon": "inventory_2",
                "collapsible": True,
                "items": [
                    {"title": _("Packages"), "icon": "inventory_2", "link": reverse_lazy("admin:packages_package_changelist")},
                ],
            },
            {
                "title": _("Commission"),
                "icon": "account_balance_wallet",
                "collapsible": True,
                "items": [
                    {"title": _("Commission Ledger"), "icon": "receipt", "link": reverse_lazy("admin:commission_commissionledger_changelist")},
                ],
            },
            {
                "title": _("Form Permissions"),
                "icon": "policy",
                "collapsible": True,
                "items": [
                    {"title": _("Access Templates"), "icon": "content_paste", "link": reverse_lazy("admin:form_permissions_accesstemplate_changelist")},
                    {"title": _("Role Field Access"), "icon": "rule", "link": reverse_lazy("admin:form_permissions_rolefieldaccess_changelist")},
                ],
            },
        ],
    },
}
