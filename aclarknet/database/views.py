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
from .forms import ClientForm
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
from .utils import entries_total
from .utils import paginate

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
    clients = Client.objects.all()
    page = request.GET.get('page')
    context['items'] = paginate(clients, page)
    return render(request, 'client_index.html', context)


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
    if request.POST:
        name = request.POST.get('name', '')
        contacts = Contact.objects.filter(last_name__contains=name)
    else:
        contacts = Contact.objects.all()
    page = request.GET.get('page')
    context['items'] = paginate(contacts, page)
    return render(request, 'contact_index.html', context)


@staff_member_required
def estimate(request, pk=None):
    context = {}

    company = Company.get_solo()
    if company:
        context['company'] = company

    estimate = get_object_or_404(Estimate, pk=pk)
    context['estimate'] = estimate

    times = Time.objects.filter(client=estimate.client, project=None)
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
def estimate_edit(request, pk=None):
    return edit(request,
                EstimateForm,
                Estimate,
                'estimate_index',
                'estimate_edit.html',
                pk=pk)


@staff_member_required
def estimate_index(request):
    context = {}
    page = request.GET.get('page')
    estimates = Estimate.objects.all()
    context['items'] = paginate(estimates, page)
    return render(request, 'estimate_index.html', context)


def home(request):
    context = {}
    context['request'] = request
    return render(request, 'home.html', context)


@staff_member_required
def invoice(request, pk=None):
    context = {}

    company = Company.get_solo()
    if company:
        context['company'] = company

    invoice = get_object_or_404(Invoice, pk=pk)
    context['invoice'] = invoice

    times = Time.objects.filter(client=invoice.client, project=invoice.project)
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
def invoice_edit(request, pk=None):
    return edit(request,
                InvoiceForm,
                Invoice,
                'invoice_index',
                'invoice_edit.html',
                pk=pk)


@staff_member_required
def invoice_index(request):
    context = {}
    invoices = Invoice.objects.all()
    page = request.GET.get('page')
    context['items'] = paginate(invoices, page)
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
    return edit(request,
                ProjectForm,
                Project,
                'project_index',
                'project_edit.html',
                pk=pk)


@staff_member_required
def project_index(request, pk=None):
    context = {}
    projects = Project.objects.all()
    page = request.GET.get('page')
    context['items'] = paginate(projects, page)
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

    url_name = 'entry_index'
    project = request.GET.get('project')
    if project:
        project = get_object_or_404(Project, pk=project)
        url_name = 'project'

    return edit(request,
                TimeForm,
                Time,
                url_name,
                'time_edit.html',
                pk=pk,
                project=project)


@login_required
def time_index(request):
    context = {}
    if request.user.is_staff:
        entries = Time.objects.all()
    else:
        entries = Time.objects.filter(user=request.user)
    page = request.GET.get('page')
    context['items'] = paginate(entries, page)
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
    return edit(request, ProfileForm, Profile, 'home', 'user_edit.html', pk=pk)


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
