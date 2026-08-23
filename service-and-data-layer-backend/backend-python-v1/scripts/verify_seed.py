import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
import django
django.setup()
from billing.models import Client
from accounts.models import User
print('Clients:', Client.objects.count())
# count users whose email contains +0199 which our seeder used
print('Users with +0199:', User.objects.filter(email__contains='+0199').count())
