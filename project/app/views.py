from django.shortcuts import render
from .models import Client

# Create your views here.


def about(request):
    return render(request, 'about.html', {})


def home(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients
    return render(request, 'home.html', context)
