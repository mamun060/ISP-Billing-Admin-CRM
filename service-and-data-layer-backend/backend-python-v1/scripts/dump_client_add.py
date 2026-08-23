import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
import django
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver','localhost','127.0.0.1']
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
# ensure admin exists
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found; creating admin/admin123')
    User.objects.create_superuser(phone='admin', password='admin123', username='admin', email='admin@example.com')
else:
    print('Superuser exists')

c = Client()
logged = c.login(phone='admin', password='admin123')
print('logged in:', logged)
resp = c.get('/admin/billing/client/add/')
print('status', resp.status_code)
out = resp.content.decode('utf-8')
outpath = os.path.join(ROOT, 'tmp', 'client_add.html')
os.makedirs(os.path.dirname(outpath), exist_ok=True)
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(out)
print('Wrote', outpath)
