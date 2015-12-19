from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django_xhtml2pdf.utils import generate_pdf
from .forms import ClientForm
from .forms import ContactForm
from .forms import EstimateForm
from .forms import InvoiceForm
from .forms import MailForm
from .forms import ProjectForm
from .forms import TaskForm
from .forms import TimeForm
from .models import Client
from .models import Company
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task
from .models import Time
from .utils import entries_total

# Create your views here.


@staff_member_required
def client(request, pk=None):
    context = {}
    client = get_object_or_404(Client, pk=pk)
    projects = Project.objects.filter(client=client)
    context['client'] = client
    context['projects'] = projects
    return render(request, 'client.html', context)


@staff_member_required
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
            return HttpResponseRedirect(reverse('client_index'))

    context['form'] = form
    return render(request, 'client_edit.html', context)


@staff_member_required
def client_index(request):
    context = {}
    clients = Client.objects.filter(active=True)

    # https://docs.djangoproject.com/en/1.9/topics/pagination/
    paginator = Paginator(clients, 10)  # Show 10 per page
    page = request.GET.get('page')
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver last page.
        clients = paginator.page(paginator.num_pages)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver first page of results.
        clients = paginator.page(1)

    context['items'] = clients

    return render(request, 'client_index.html', context)


@staff_member_required
def contact(request, pk=None):
    context = {}
    contact = get_object_or_404(Contact, pk=pk)
    context['contact'] = contact
    return render(request, 'contact.html', context)


@staff_member_required
def contact_edit(request, pk=None):
    context = {}
    contact = None

    if pk is None:
        form = ContactForm()
    else:
        contact = get_object_or_404(Contact, pk=pk)
        form = ContactForm(instance=contact)

    if request.method == 'POST':

        if pk is None:
            form = ContactForm(request.POST)
        else:
            form = ContactForm(request.POST, instance=contact)

        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect(reverse('contact_index'))

    context['contact'] = contact
    context['form'] = form
    return render(request, 'contact_edit.html', context)


@staff_member_required
def contact_index(request):
    context = {}
    contacts = Contact.objects.filter(active=True)

    paginator = Paginator(contacts, 10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(paginator.num_pages)
    except EmptyPage:
        contacts = paginator.page(1)

    context['items'] = contacts

    return render(request, 'contact_index.html', context)


@staff_member_required
def estimate(request, pk=None):
    context = {}

    company = Company.objects.get()
    if company:
        context['company'] = company

    estimate = get_object_or_404(Estimate, pk=pk)
    context['estimate'] = estimate

    times = Time.objects.filter(client=estimate.client)
    entries, total = entries_total(times)

    context['entries'] = entries
    context['total'] = total

    pdf = request.GET.get('pdf')
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        return generate_pdf('estimate_table.html',
                            context=context,
                            file_object=response)
    else:
        return render(request, 'estimate.html', context)


@staff_member_required
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


@staff_member_required
def estimate_index(request):
    context = {}
    estimates = Estimate.objects.all()
    context['estimates'] = estimates
    return render(request, 'estimate_index.html', context)


def home(request):
    context = {}
    clients = Client.objects.all()
    context['request'] = request
    context['clients'] = clients
    return render(request, 'home.html', context)


@staff_member_required
def invoice(request, pk=None):
    context = {}

    company = Company.objects.get()
    if company:
        context['company'] = company

    invoice = get_object_or_404(Estimate, pk=pk)
    context['invoice'] = invoice

    times = Time.objects.filter(client=invoice.client)
    entries, total = entries_total(times)

    context['entries'] = entries
    context['total'] = total

    pdf = request.GET.get('pdf')
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        return generate_pdf('invoice_table.html',
                            context=context,
                            file_object=response)
    else:
        return render(request, 'invoice.html', context)


@staff_member_required
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


@staff_member_required
def invoice_index(request):
    client = None
    context = {}
    invoices = []
    for invoice in Invoice.objects.all():
        clients = Client.objects.filter(project=invoice.project)
        if len(clients) > 0:
            client = clients[0]
        invoices.append([invoice, client])
    context['invoices'] = invoices

    return render(request, 'invoice_index.html', context)


@staff_member_required
def project(request, pk=None):
    context = {}
    project = get_object_or_404(Project, pk=pk)
    times = Time.objects.filter(project=project)
    context['project'] = project
    context['times'] = times
    return render(request, 'project.html', context)


@staff_member_required
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


@staff_member_required
def project_index(request, pk=None):
    context = {}
    projects = Project.objects.all()
    context['projects'] = projects
    return render(request, 'project_index.html', context)


@staff_member_required
def task(request, pk=None):
    context = {}
    task = get_object_or_404(Task, pk=pk)
    context['task'] = task
    return render(request, 'task.html', context)


@staff_member_required
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


@staff_member_required
def task_index(request):
    context = {}
    tasks = Task.objects.all()
    context['tasks'] = tasks
    return render(request, 'task_index.html', context)


@login_required
def time(request, pk=None):
    context = {}
    entry = get_object_or_404(Time, pk=pk)
    context['entry'] = entry
    return render(request, 'time.html', context)


@login_required
def time_edit(request, pk=None):
    context = {}

    project = request.GET.get('project', None)

    if pk is None:
        if project is None:
            form = TimeForm()
        else:
            project = get_object_or_404(Project, pk=project)
            time = Time(project=project)
            form = TimeForm(instance=time)
    else:
        time = get_object_or_404(Time, pk=pk)
        form = TimeForm(instance=time)

    if request.method == 'POST':

        if pk is None:
            form = TimeForm(request.POST)
        else:
            time = get_object_or_404(Time, pk=pk)
            form = TimeForm(request.POST, instance=time)

        if form.is_valid():
            time = form.save()
            return HttpResponseRedirect(reverse('entry_index'))

    context['form'] = form
    return render(request, 'time_edit.html', context)


@login_required
def time_index(request):
    context = {}
    entries = Time.objects.all()
    context['entries'] = entries
    return render(request, 'time_index.html', context)


@login_required
def user(request, pk=None):
    context = {}
    user = get_object_or_404(User, pk=pk)
    context['request'] = request
    context['user'] = user

    if request.user.pk == int(pk) or request.user.is_staff:
        return render(request, 'user.html', context)
    else:
        return HttpResponseRedirect(reverse('home'))


@staff_member_required
def user_index(request):
    context = {}
    users = User.objects.all()
    context['users'] = users
    return render(request, 'user_index.html', context)


@staff_member_required
def user_mail(request, pk=None):
    context = {}
    recipients = []
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = MailForm(request.POST)
        if form.is_valid():
            sender = settings.DEFAULT_FROM_EMAIL
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipients.append(user.email)
            send_mail(subject,
                      message,
                      sender,
                      recipients,
                      fail_silently=False)
            messages.add_message(request, messages.SUCCESS, 'Success!')
            return HttpResponseRedirect(reverse('user_index'))
    else:
        form = MailForm()
    context['form'] = form
    context['user'] = user
    return render(request, 'user_mail.html', context)
