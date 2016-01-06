from django.test import TestCase

# Create your tests here.

from .models import Client


class ClientTestCase(TestCase):
    def setUp(self):
        Client.objects.create(name="client-1", active=True)

    def test_client_is_active(self):
        client = Client.objects.get(name="client-1")
        self.assertEqual(client.active, True)
