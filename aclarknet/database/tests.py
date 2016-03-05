from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client as HttpClient
from .models import Client
from .forms import ClientForm
from .utils import edit

# Create your tests here.


class ClientTestCase(TestCase):
    def setUp(self):
        Client.objects.create(name="client-1", active=True)

    def test_is_active(self):
        client = Client.objects.get(name="client-1")
        self.assertEqual(client.active, True)

    def test_is_editable(self):
        """
        request, form_model, model, url_name, template
        """
        client = Client.objects.get(name="client-1")

        user = User(is_staff=True)
        user.save()
        httpclient = HttpClient()
        httpclient.force_login(user)

        response = httpclient.post('/client/%s/edit' % client.pk)

        self.assertEqual(response.status_code, 302)

        edit(response.wsgi_request, ClientForm, Client, 'client_index', 'client_edit.html')
