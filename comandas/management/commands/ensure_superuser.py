import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cria o primeiro superusuário a partir de variáveis de ambiente, se necessário.'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Superusuário já existe.')
            return

        username = os.environ.get('INITIAL_SUPERUSER_USERNAME', '').strip()
        password = os.environ.get('INITIAL_SUPERUSER_PASSWORD', '')
        email = os.environ.get('INITIAL_SUPERUSER_EMAIL', '').strip()
        if not username or not password:
            raise CommandError(
                'Defina INITIAL_SUPERUSER_USERNAME e INITIAL_SUPERUSER_PASSWORD antes do primeiro deploy.'
            )
        if User.objects.filter(username=username).exists():
            raise CommandError('O usuário inicial já existe, mas não é superusuário.')

        user = User(username=username, email=email)
        try:
            validate_password(password, user)
        except Exception as error:
            raise CommandError('A senha inicial não atende aos requisitos: ' + ' '.join(error.messages))
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Superusuário {username!r} criado.'))
