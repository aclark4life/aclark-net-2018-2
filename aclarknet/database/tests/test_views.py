from ..models import Contact
from ..forms import ContactForm
from ..models import Client
from ..forms import ClientForm
from ..utils import edit
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client as HttpClient

# Create your tests here.


class ContactTestCase(TestCase):

    def setUp(self):
        Contact.objects.create(active=True, id=1, )


    def test_edit(self):
        """
        :params: request, form_model, model, url_name, template
        """
        user = User(is_staff=True)
        user.save()

        httpclient = HttpClient()
        httpclient.force_login(user)

        contact = Contact.objects.get(id=1)
        response = httpclient.get('/contact/%s/edit' % contact.pk)
        self.assertEqual(response.status_code, 200)
        request = response.wsgi_request

        edit(request,
             ContactForm,
             Contact,
             'contact_index',
             'contact_edit.html',
             pk=contact.id)


class ClientTestCase(TestCase):

    def setUp(self):
        Client.objects.create(active=True,
                              address="1234 Street",
                              description="The First Client",
                              name="Client 1", )

    def test_edit(self):
        """
        :params: request, form_model, model, url_name, template
        """
        user = User(is_staff=True)
        user.save()

        httpclient = HttpClient()
        httpclient.force_login(user)

        client = Client.objects.get(name="Client 1")
        response = httpclient.get('/client/%s/edit' % client.pk)
        self.assertEqual(response.status_code, 200)
        request = response.wsgi_request

        edit(request,
             ClientForm,
             Client,
             'client_index',
             'client_edit.html',
             pk=client.id)
