from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import ClientForm
from .forms import ProjectForm
from .models import Client
from .models import Project

# Create your views here.


def about(request):
    return render(request, 'about.html', {})


def client(request, pk=None):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    context['client'] = client
    return render(request, 'client.html', context)


def client_edit(request, pk=None):
    context = {}

    if pk is None:
        form = ClientForm()
    else:
        client = get_object_or_404(Client, pk=pk)
        form = ClientForm(instance=client)

    if request.method == 'POST':

        if pk is None:
            form = ClientForm(request.POST)
        else:
            form = ClientForm(request.POST, instance=client)

        if form.is_valid():
            client = form.save()
            return HttpResponseRedirect(reverse('home'))

    context['form'] = form
    return render(request, 'client_edit.html', context)


def contact(request):
    return render(request, 'contact.html', {})


def home(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients
    return render(request, 'home.html', context)


def project(request, pk=None):
    context = {}
    project = get_object_or_404(Project, pk=pk)
    context['project'] = project
    return render(request, 'project.html', context)


def project_edit(request, pk=None):
    context = {}

    if pk is None:
        form = ProjectForm()
    else:
        client = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=client)

    if request.method == 'POST':

        if pk is None:
            form = ProjectForm(request.POST)
        else:
            form = ProjectForm(request.POST, instance=client)

        if form.is_valid():
            client = form.save()
            return HttpResponseRedirect(reverse('home'))

    context['form'] = form
    return render(request, 'project_edit.html', context)
