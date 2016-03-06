from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client as HttpClient
from .models import Client
from .forms import ClientForm
from .utils import edit

# Create your tests here.


class ClientTestCase(TestCase):
    def setUp(self):
        Client.objects.create(active=True,
                              address="1234 Street",
                              description="The First Client",
                              name="Client 1",
                              )

    def test_create(self):
        client = Client.objects.get(name="Client 1")
        self.assertEqual(client.active, True)
        self.assertEqual(client.address, "1234 Street")
        self.assertEqual(client.description, "The First Client")
        self.assertEqual(client.name, "Client 1")

    def test_edit(self):
        """
        :params: request, form_model, model, url_name, template
        """
        user = User(is_staff=True)
        user.save()

        httpclient = HttpClient()
        httpclient.force_login(user)

        client = Client.objects.get(name="Client 1")
        response = httpclient.post('/client/%s/edit' % client.pk)
        self.assertEqual(response.status_code, 302)

        edit(response.wsgi_request, ClientForm, Client, 'client_index', 'client_edit.html')
