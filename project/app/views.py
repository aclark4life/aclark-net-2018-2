from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import ClientForm
from .forms import EstimateForm
from .forms import InvoiceForm
from .forms import ProjectForm
from .forms import TaskForm
from .models import Client
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task

# Create your views here.


def about(request):
    return render(request, 'about.html', {})


def client(request, pk=None):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    projects = Project.objects.filter(client=client)
    context['client'] = client
    context['projects'] = projects
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


def estimate(request, pk=None):
    context = {}
    estimate = get_object_or_404(Estimate, pk=pk)
    tasks = Task.objects.filter(client=estimate.client)
    context['estimate'] = estimate
    context['tasks'] = tasks
    return render(request, 'estimate.html', context)


def estimate_edit(request, client=None, pk=None):
    context = {}

    if pk is None:
        if client is None:
            form = EstimateForm()
        else:
            client = get_object_or_404(Client, pk=client)
            estimate = Estimate(client=client)
            form = EstimateForm(instance=estimate)
    else:
        estimate = get_object_or_404(Estimate, pk=pk)
        form = EstimateForm(instance=estimate)

    if request.method == 'POST':

        if pk is None:
            form = EstimateForm(request.POST)
        else:
            estimate = get_object_or_404(Estimate, pk=pk)
            form = EstimateForm(request.POST, instance=estimate)

        if form.is_valid():
            estimate = form.save()
            return HttpResponseRedirect(reverse('estimate_index'))

    context['form'] = form
    return render(request, 'estimate_edit.html', context)


def estimate_index(request):
    context = {}
    estimates = Estimate.objects.all()
    context['estimates'] = estimates
    return render(request, 'estimate_index.html', context)


def home(request):
    context = {}
    clients = Client.objects.all()
    context['clients'] = clients
    return render(request, 'home.html', context)


def invoice(request, pk=None):
    context = {}
    invoice = get_object_or_404(Invoice, pk=pk)
    project = Project.objects.filter(invoice=invoice)
    client = Client.objects.filter(project=project)[0]
    tasks = Task.objects.filter(client=client)
    context['client'] = client
    context['invoice'] = invoice
    context['project'] = project
    context['tasks'] = tasks
    return render(request, 'invoice.html', context)


def invoice_edit(request, client=None, pk=None):
    context = {}

    if pk is None:
        if client is None:
            form = InvoiceForm()
        else:
            client = get_object_or_404(Client, pk=client)
            invoice = Invoice(client=client)
            form = InvoiceForm(instance=invoice)
    else:
        invoice = get_object_or_404(Invoice, pk=pk)
        form = InvoiceForm(instance=invoice)

    if request.method == 'POST':

        if pk is None:
            form = InvoiceForm(request.POST)
        else:
            invoice = get_object_or_404(Invoice, pk=pk)
            form = InvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save()
            return HttpResponseRedirect(reverse('invoice_index'))

    context['form'] = form
    return render(request, 'invoice_edit.html', context)


def invoice_index(request):
    context = {}
    invoices = []
    for invoice in Invoice.objects.all():
        client = Client.objects.filter(project=invoice.project)[0]
        invoices.append([invoice, client])
    context['invoices'] = invoices

    return render(request, 'invoice_index.html', context)


def project(request, pk=None):
    context = {}
    project = get_object_or_404(Project, pk=pk)
    tasks = Task.objects.filter(project=project)
    context['project'] = project
    context['tasks'] = tasks
    return render(request, 'project.html', context)


def project_edit(request, pk=None):
    context = {}

    client = request.GET.get('client', None)

    if pk is None:
        if client is None:
            form = ProjectForm()
        else:
            client = get_object_or_404(Client, pk=client)
            project = Project(client=client)
            form = ProjectForm(instance=project)
    else:
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=project)

    if request.method == 'POST':

        if pk is None:
            form = ProjectForm(request.POST)
        else:
            project = get_object_or_404(Project, pk=pk)
            form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save()
            return HttpResponseRedirect(reverse('project_index'))

    context['form'] = form
    return render(request, 'project_edit.html', context)


def project_index(request, pk=None):
    context = {}
    projects = Project.objects.all()
    context['projects'] = projects
    return render(request, 'project_index.html', context)


def task(request, pk=None):
    context = {}
    task = get_object_or_404(Task, pk=pk)
    context['task'] = task
    return render(request, 'task.html', context)


def task_edit(request, pk=None):
    context = {}

    project = request.GET.get('project', None)

    if pk is None:
        if project is None:
            form = TaskForm()
        else:
            project = get_object_or_404(Project, pk=project)
            task = Task(project=project)
            form = TaskForm(instance=task)
    else:
        task = get_object_or_404(Task, pk=pk)
        form = TaskForm(instance=task)

    if request.method == 'POST':

        if pk is None:
            form = TaskForm(request.POST)
        else:
            task = get_object_or_404(Task, pk=pk)
            form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save()
            return HttpResponseRedirect(reverse('task_index'))

    context['form'] = form
    return render(request, 'task_edit.html', context)


def task_index(request):
    context = {}
    tasks = Task.objects.all()
    context['tasks'] = tasks
    return render(request, 'task_index.html', context)
