from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
import os


class Command(BaseCommand):
    help = "Dump the admin client add page HTML to tmp/client_add.html"

    def handle(self, *args, **options):
        settings.ALLOWED_HOSTS = list(getattr(settings, 'ALLOWED_HOSTS', [])) + ['testserver', 'localhost', '127.0.0.1']
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('No superuser found; creating admin/admin123')
            User.objects.create_superuser(phone='admin', password='admin123', username='admin', email='admin@example.com')
        else:
            self.stdout.write('Superuser exists')

        c = Client()
        logged = c.login(phone='admin', password='admin123')
        self.stdout.write(f'logged in: {logged}')
        resp = c.get('/admin/billing/client/add/')
        self.stdout.write(f'status: {resp.status_code}')
        out = resp.content.decode('utf-8')
        outpath = os.path.join(os.getcwd(), 'tmp', 'client_add.html')
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(out)
        self.stdout.write(f'Wrote {outpath}')
