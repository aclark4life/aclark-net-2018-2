from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import Client

# Create your views here.


def about(request):
    return render(request, 'about.html', {})


def client(request, pk):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'client.html', context)


def home(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients
    return render(request, 'home.html', context)
