from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from comandas.models import Comanda


@override_settings(SECURE_SSL_REDIRECT=False)
class AccessAndAnalyticsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='operador', password='senha-de-teste-segura-123'
        )
        self.staff = get_user_model().objects.create_user(
            username='gestor', password='senha-de-teste-segura-456', is_staff=True
        )

    def test_operational_views_require_login(self):
        protected_urls = [
            reverse('index'), reverse('nova_comanda'), reverse('historico'),
            reverse('comanda_detalhe', args=[999]), reverse('imprimir_comanda', args=[999]),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('login'), response.url)

    def test_healthcheck_is_available_without_login(self):
        response = self.client.get(reverse('healthcheck'))
        self.assertEqual(response.status_code, 204)

    def test_dashboard_requires_staff_and_formats_hour(self):
        comanda = Comanda.objects.create()
        comanda.status = Comanda.STATUS_FECHADA
        comanda.fechada_em = timezone.now()
        comanda.save()

        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.staff)
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.context['pico_por_hora'][0]['hora'], r'^\d{2}:00$')

    def test_login_is_locked_after_five_failed_attempts(self):
        for _ in range(5):
            response = self.client.post(reverse('login'), {
                'username': 'operador', 'password': 'senha-incorreta',
            }, REMOTE_ADDR='198.51.100.4')
        self.assertContains(response, 'Login temporariamente bloqueado')

        response = self.client.post(reverse('login'), {
            'username': 'operador', 'password': 'senha-de-teste-segura-123',
        }, REMOTE_ADDR='198.51.100.4')
        self.assertContains(response, 'Login temporariamente bloqueado')
