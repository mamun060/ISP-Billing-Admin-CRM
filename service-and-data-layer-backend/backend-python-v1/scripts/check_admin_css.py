import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
import django
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver','localhost']
from django.test import Client
c = Client()
resp = c.get('/admin/login/')
html = resp.content.decode('utf-8')
found1 = 'custom_sidebar.css' in html
found2 = 'custom_forms.css' in html
print('Status', resp.status_code)
print('custom_sidebar.css found:', found1)
print('custom_forms.css found:', found2)
