from ..models import Contact
from ..models import Client
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.


class ContactTestCase(TestCase):

    def setUp(self):
        Contact.objects.create(active=True, first_name="Alex", last_name="Clark", pk=1)

    def test_create(self):
        contact = Contact.objects.get(pk=1)
        self.assertEqual(contact.active, True)
        self.assertEqual(contact.first_name, "Alex")
        self.assertEqual(contact.last_name, "Clark")



class ClientTestCase(TestCase):

    def setUp(self):
        Client.objects.create(active=True,
                              address="1234 Street",
                              description="The First Client",
                              name="Client 1", )

    def test_create(self):
        client = Client.objects.get(name="Client 1")
        self.assertEqual(client.active, True)
        self.assertEqual(client.address, "1234 Street")
        self.assertEqual(client.description, "The First Client")
        self.assertEqual(client.name, "Client 1")
