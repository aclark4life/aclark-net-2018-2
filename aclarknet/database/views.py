from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django_xhtml2pdf.utils import generate_pdf
from itertools import chain
from .forms import ClientForm
from .forms import CompanyForm
from .forms import ContactForm
from .forms import EstimateForm
from .forms import InvoiceForm
from .forms import MailForm
from .forms import ProfileForm
from .forms import ProjectForm
from .forms import TaskForm
from .forms import TimeForm
from .models import Client
from .models import Company
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Profile
from .models import Project
from .models import Task
from .models import Time
from .utils import edit
from .utils import dashboard_total
from .utils import entries_total
from .utils import last_month
from .utils import search

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
    return edit(request,
                ClientForm,
                Client,
                'client_index',
                'client_edit.html',
                pk=pk)


@staff_member_required
def client_index(request):
    context = {}
    fields = ('address', 'name')
    order_by = '-pk'
    items = search(request, Client, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'client_index.html', context)


@staff_member_required
def company_edit(request, pk=None):
    return edit(request,
                CompanyForm,
                Company,
                'company',
                'company_edit.html',
                pk=1)


@staff_member_required
def company(request):
    context = {}
    company = Company.get_solo()
    context['company'] = company
    return render(request, 'company.html', context)


@staff_member_required
def contact(request, pk=None):
    context = {}
    contact = get_object_or_404(Contact, pk=pk)
    context['contact'] = contact
    return render(request, 'contact.html', context)


@staff_member_required
def contact_edit(request, pk=None):
    return edit(request,
                ContactForm,
                Contact,
                'contact_index',
                'contact_edit.html',
                pk=pk)


@staff_member_required
def contact_index(request):
    context = {}
    fields = ('first_name', 'last_name', 'email')
    order_by = '-pk'
    items = search(request, Contact, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'contact_index.html', context)


@staff_member_required
def contact_mail(request, pk=None):
    context = {}
    recipients = []
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = MailForm(request.POST)
        if form.is_valid():
            sender = settings.DEFAULT_FROM_EMAIL
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipients.append(contact.email)
            send_mail(subject,
                      message,
                      sender,
                      recipients,
                      fail_silently=False)
            messages.add_message(request, messages.SUCCESS, 'Success!')
            return HttpResponseRedirect(reverse('contact_index'))
    else:
        form = MailForm()
    context['form'] = form
    context['contact'] = contact
    return render(request, 'contact_mail.html', context)


@staff_member_required
def estimate(request, pk=None):
    context = {}

    company = Company.get_solo()
    if company:
        context['company'] = company

    estimate = get_object_or_404(Estimate, pk=pk)

    document_id = str(estimate.document_id)
    document_type = estimate._meta.verbose_name
    document_type_upper = document_type.upper()
    document_type_title = document_type.title()

    context['document'] = estimate
    context['document_type_upper'] = document_type_upper
    context['document_type_title'] = document_type_title

    times_client = Time.objects.filter(client=estimate.client,
                                       estimate=None,
                                       project=None)
    times_estimate = Time.objects.filter(estimate=estimate)
    times = chain(times_client, times_estimate)

    entries, subtotal, paid_amount, hours, amount = entries_total(times)
    context['entries'] = entries
    context['amount'] = amount
    context['paid_amount'] = paid_amount
    context['subtotal'] = subtotal
    context['hours'] = hours

    pdf = request.GET.get('pdf')
    context['pdf'] = pdf
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        return generate_pdf('entry_table.html',
                            context=context,
                            file_object=response)
    else:
        return render(request, 'estimate.html', context)


@staff_member_required
def estimate_edit(request, pk=None):
    amount = request.GET.get('amount')
    paid_amount = request.GET.get('paid_amount')
    subtotal = request.GET.get('subtotal')
    times = request.GET.get('times')
    company = Company.get_solo()

    if times:
        estimate = get_object_or_404(Estimate, pk=pk)
        times = Time.objects.filter(pk__in=[int(i) for i in times.split(',')])
        for entry in times:
            entry.estimate = estimate
            entry.save()

    return edit(request,
                EstimateForm,
                Estimate,
                'estimate_index',
                'estimate_edit.html',
                amount=amount,
                paid_amount=paid_amount,
                pk=pk,
                subtotal=subtotal,
                company=company)


@staff_member_required
def estimate_index(request):
    context = {}
    fields = ('subject', )
    order_by = '-pk'
    items = search(request, Estimate, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'estimate_index.html', context)


def home(request):
    context = {}
    clients = Client.objects.all()
    clients_active = Client.objects.filter(active=True)
    company = Company.get_solo()
    contacts = Contact.objects.all()
    contacts_active = Contact.objects.filter(active=True)
    projects = Project.objects.all()
    projects_active = Project.objects.filter(active=True)
    tasks = Task.objects.all()
    tasks_active = Task.objects.filter(active=True)
    times = Time.objects.all()
    invoices = Invoice.objects.all()
    invoices_active = Invoice.objects.filter(
        issue_date__gt=last_month()).order_by('issue_date')
    gross, net = dashboard_total(invoices_active)
    estimates = Estimate.objects.all()
    context['clients'] = clients
    context['clients_active'] = clients_active
    context['company'] = company
    context['contacts'] = contacts
    context['contacts_active'] = contacts_active
    context['projects'] = projects
    context['projects_active'] = projects_active
    context['tasks'] = tasks
    context['tasks_active'] = tasks_active
    context['times'] = times
    context['invoices'] = invoices
    context['invoices_active'] = invoices_active
    context['gross'] = gross
    context['net'] = net
    context['estimates'] = estimates
    context['request'] = request

    return render(request, 'home.html', context)


@staff_member_required
def invoice(request, pk=None):
    context = {}
    order_by = '-date'

    company = Company.get_solo()
    if company:
        context['company'] = company

    invoice = get_object_or_404(Invoice, pk=pk)

    document_id = str(invoice.document_id)
    document_type = invoice._meta.verbose_name
    document_type_upper = document_type.upper()
    document_type_title = document_type.title()

    context['document'] = invoice
    context['document_type_upper'] = document_type_upper
    context['document_type_title'] = document_type_title

    times_project = Time.objects.filter(invoiced=False,
                                        project=invoice.project,
                                        invoice=None).order_by(order_by)
    times_invoice = Time.objects.filter(invoice=invoice)
    times = chain(times_project, times_invoice)

    entries, subtotal, paid_amount, hours, amount = entries_total(times)
    context['entries'] = entries
    context['amount'] = amount
    context['paid_amount'] = paid_amount
    context['subtotal'] = subtotal
    context['hours'] = hours

    context['invoice'] = True

    pdf = request.GET.get('pdf')
    context['pdf'] = pdf
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        if company.name:
            company = company.name.replace('.', '_')
            company = company.replace(', ', '_')
            company = company.upper()
        filename = '_'.join([document_type_upper, document_id, company])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf('entry_table.html',
                            context=context,
                            file_object=response)
    else:
        return render(request, 'invoice.html', context)


@staff_member_required
def invoice_edit(request, pk=None):
    amount = request.GET.get('amount')
    paid_amount = request.GET.get('paid_amount')
    subtotal = request.GET.get('subtotal')
    times = request.GET.get('times')
    company = Company.get_solo()

    if pk:
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.project:
            if invoice.project.client and not invoice.client:
                invoice.client = invoice.project.client
                invoice.save()

    if times:
        invoice = get_object_or_404(Invoice, pk=pk)
        times = Time.objects.filter(pk__in=[int(i) for i in times.split(',')])
        for entry in times:
            entry.invoice = invoice
            entry.save()

    return edit(request,
                InvoiceForm,
                Invoice,
                'invoice_index',
                'invoice_edit.html',
                amount=amount,
                paid_amount=paid_amount,
                pk=pk,
                subtotal=subtotal,
                company=company)


@staff_member_required
def invoice_index(request):
    context = {}
    fields = ('subject', )
    order_by = '-pk'
    items = search(request, Invoice, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'invoice_index.html', context)


@staff_member_required
def project(request, pk=None):
    context = {}
    project = get_object_or_404(Project, pk=pk)
    times = Time.objects.filter(project=project).order_by('-date')
    context['project'] = project
    context['times'] = times
    return render(request, 'project.html', context)


@staff_member_required
def project_edit(request, pk=None):
    url_name = 'project_index'
    client = request.GET.get('client')
    if client:
        client = get_object_or_404(Client, pk=client)
        url_name = 'client'
    return edit(request,
                ProjectForm,
                Project,
                url_name,
                'project_edit.html',
                client=client,
                pk=pk)


@staff_member_required
def project_index(request, pk=None):
    context = {}
    fields = ('id', 'name')
    order_by = '-start_date'
    items = search(request, Project, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'project_index.html', context)


@staff_member_required
def task(request, pk=None):
    context = {}
    task = get_object_or_404(Task, pk=pk)
    context['task'] = task
    return render(request, 'task.html', context)


@staff_member_required
def task_edit(request, pk=None):
    return edit(request, TaskForm, Task, 'task_index', 'task_edit.html', pk=pk)


@staff_member_required
def task_index(request):
    context = {}
    order_by = '-pk'
    fields = ('name', )
    items = search(request, Task, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'task_index.html', context)


@login_required
def time(request, pk=None):
    context = {}
    entry = get_object_or_404(Time, pk=pk)
    if not entry.user and not request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    if entry.user:
        if (not entry.user.username == request.user.username and
                not request.user.is_staff):
            return HttpResponseRedirect(reverse('admin:index'))
    context['entry'] = entry
    return render(request, 'time.html', context)


@login_required
def time_edit(request, pk=None):

    url_name = 'entry_index'

    client = request.GET.get('client')
    project = request.GET.get('project')

    if client:
        client = get_object_or_404(Client, pk=client)
        url_name = 'estimate_index'

    if project:
        project = get_object_or_404(Project, pk=project)
        url_name = 'project'

    try:
        task = Task.objects.filter(active=True).latest('pk')
    except Task.DoesNotExist:
        task = None

    return edit(request,
                TimeForm,
                Time,
                url_name,
                'time_edit.html',
                pk=pk,
                client=client,
                project=project,
                task=task)


@login_required
def time_index(request):
    context = {}
    fields = ('notes', )
    order_by = '-pk'
    items = search(request, Time, fields, order_by=order_by)
    context['items'] = items
    return render(request, 'time_index.html', context)


@login_required
def user(request, pk=None):
    context = {}

    user = get_object_or_404(User, pk=pk)
    profile = Profile.objects.get_or_create(user=user)[0]

    context['profile'] = profile
    context['request'] = request
    context['user'] = user

    if request.user.pk == int(pk) or request.user.is_staff:
        return render(request, 'user.html', context)
    else:
        return HttpResponseRedirect(reverse('home'))


@login_required
def user_edit(request, pk=None):
    context = {}
    user = get_object_or_404(User, pk=pk)
    context['user'] = user
    return edit(request,
                ProfileForm,
                Profile,
                'home',
                'user_edit.html',
                pk=pk,
                context=context)


@staff_member_required
def user_index(request):
    context = {}
    items = User.objects.all()
    context['items'] = items
    return render(request, 'user_index.html', context)
