from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = 'Create initial superuser if not exists'

    def handle(self, *args, **options):
        User = get_user_model()

        email = config('ADMIN_EMAIL')
        password = config('ADMIN_PASSWORD')

        if not email or not password:
            self.stdout.write('Admin credentials not set')
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write('Admin already exists')
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write('Admin created')
