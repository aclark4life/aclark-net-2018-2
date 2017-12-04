from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from faker import Faker
from rest_framework import viewsets
from .forms import AdminProfileForm
from .forms import AdminTimeForm
from .forms import ClientForm
from .forms import ContactForm
from .forms import ContractForm
from .forms import EstimateForm
from .forms import FileForm
from .forms import InvoiceForm
from .forms import NewsletterForm
from .forms import NoteForm
from .forms import ProfileForm
from .forms import ProjectForm
from .forms import ProposalForm
from .forms import ReportForm
from .forms import ServiceForm
from .forms import SettingsAppForm
from .forms import SettingsCompanyForm
from .forms import SettingsContractForm
from .forms import TaskForm
from .forms import TimeForm
from .models import Client
from .models import Contact
from .models import Contract
from .models import DashboardItem
from .models import Estimate
from .models import File
from .models import Invoice
from .models import Log
from .models import Newsletter
from .models import Note
from .models import Profile
from .models import Project
from .models import Proposal
from .models import Report
from .models import Service
from .models import SettingsApp
from .models import SettingsCompany
from .models import SettingsContract
from .models import Testimonial
from .models import Task
from .models import Time
from .export import render_pdf
from .info import has_profile
from .plot import get_plot
from .serializers import ClientSerializer
from .serializers import ProfileSerializer
from .serializers import ServiceSerializer
from .serializers import TestimonialSerializer
from .utils import edit
from .utils import get_index_items
from .utils import get_page_items

fake = Faker()
message = "Sorry, you are not allowed to see that."

# Create your views here.


class ClientViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Client.objects.filter(published=True).order_by('name')
    serializer_class = ClientSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Service.objects.filter(active=True).order_by('name')
    serializer_class = ServiceSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Testimonial.objects.filter(active=True).order_by('-issue_date')
    serializer_class = TestimonialSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = Profile.objects.filter(
        published=True).order_by('user__first_name')
    serializer_class = ProfileSerializer


def get_company_name(model):
    company = model.get_solo()
    if company.name:
        company_name = company.name
    else:
        company_name = fake.text()
    # Ghetto
    company_name = company_name.replace('.', '_')
    company_name = company_name.replace(', ', '_')
    company_name = company_name.replace('#', '_')
    company_name = company_name.replace('-', '_')
    company_name = company_name.replace('(', '_')
    company_name = company_name.replace(')', '_')
    company_name = company_name.replace(' ', '_')
    company_name = company_name.upper()
    return company_name


@staff_member_required
def client_view(request, pk=None):
    order_by = {
        'project': ('-updated', ),
    }
    context = get_page_items(
        app_settings_model=SettingsApp,
        contact_model=Contact,
        contract_model=Contract,
        model=Client,
        order_by=order_by,
        pk=pk,
        project_model=Project,
        request=request)
    return render(request, 'client_view.html', context)


@staff_member_required
def client_edit(request, pk=None):
    return edit(request, form_model=ClientForm, model=Client, pk=pk)


@staff_member_required
def client_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Client,
        order_by=('-active', 'name'),
        request=request,
        search_fields=('address', 'name'))
    return render(request, 'client_index.html', context)


@staff_member_required
def contact_view(request, pk=None):
    context = get_page_items(
        app_settings_model=SettingsApp, model=Contact, pk=pk, request=request)
    return render(request, 'contact_view.html', context)


@staff_member_required
def contact_edit(request, pk=None):
    return edit(
        request,
        form_model=ContactForm,
        model=Contact,
        client_model=Client,
        user_model=User,
        pk=pk)


@staff_member_required
def contact_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Contact,
        order_by=('-active', 'last_name', 'first_name'),
        request=request,
        search_fields=('first_name', 'last_name', 'email', 'notes', 'pk'))
    return render(request, 'contact_index.html', context)


@staff_member_required
def contract_view(request, pk=None):
    """
    """
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        model=Contract,
        pk=pk,
        time_model=Time,
        request=request)
    return render(request, 'contract_view.html', context)


@staff_member_required
def contract_edit(request, pk=None):
    """
    """
    return edit(request, form_model=ContractForm, model=Contract, pk=pk)


@staff_member_required
def contract_index(request):
    """
    """
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Contract,
        request=request,
        order_by=('-updated', ))
    return render(request, 'contract_index.html', context)


def error(request):
    """
    """
    raise


@staff_member_required
def estimate_view(request, pk=None):
    order_by = {
        'time': ('updated', ),
    }
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        model=Estimate,
        order_by=order_by,
        pk=pk,
        project_model=Project,
        time_model=Time,
        request=request)
    return render(request, 'estimate_view.html', context)


@staff_member_required
def estimate_edit(request, pk=None):
    return edit(
        request,
        form_model=EstimateForm,
        model=Estimate,
        company_model=SettingsCompany,
        project_model=Project,
        pk=pk,
        user_model=User)


@staff_member_required
def estimate_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Estimate,
        order_by=('-issue_date', ),
        search_fields=('subject', ),
        request=request)
    return render(request, 'estimate_index.html', context)


@staff_member_required
def file_view(request, pk=None):
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        model=File,
        pk=pk,
        request=request)
    return render(request, 'file_view.html', context)


@staff_member_required
def file_edit(request, pk=None):
    return edit(
        request,
        form_model=FileForm,
        model=File,
        company_model=SettingsCompany,
        pk=pk,
    )


@staff_member_required
def file_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=File,
        order_by=('-updated', ),
        request=request,
    )
    return render(request, 'file_index.html', context)


def home(request):
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        columns_visible={
            'note': {
                'due': 'false',
                'hidden': 'false',
                'note': 'false',
            },
            'invoice': {
                'paid': 'false',
            },
        },
        dashboard_item_model=DashboardItem,
        estimate_model=Estimate,
        invoice_model=Invoice,
        note_model=Note,
        order_by={
            'invoice': ('-amount', ),
            'estimate': ('-issue_date', ),
            'note': ('-active', '-updated', 'tags'),
            'project': ('-updated', ),
            'report': ('date', ),
            'time': ('-updated', ),
        },
        project_model=Project,
        time_model=Time,
        report_model=Report,
        request=request)
    return render(request, 'home.html', context)


@staff_member_required
def invoice_view(request, pk=None):
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        model=Invoice,
        order_by={'time': ('date', 'updated')},  # For time entries
        pk=pk,
        request=request,
        time_model=Time)
    if context['pdf']:
        company_name = get_company_name(SettingsCompany)
        return render_pdf(request, 'invoice_pdf.html', context, pk=pk, company_name=company_name)
    else:
        return render(request, 'invoice_view.html', context)


@staff_member_required
def invoice_edit(request, pk=None):
    return edit(
        request,
        form_model=InvoiceForm,
        model=Invoice,
        company_model=SettingsCompany,
        project_model=Project,
        pk=pk,
    )


@staff_member_required
def invoice_index(request):
    search_fields = (
        'client__name',
        'issue_date',
        'project__name',
        'subject',
    )
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Invoice,
        order_by=('-issue_date', ),
        request=request,
        search_fields=search_fields)
    return render(request, 'invoice_index.html', context)


def login(request):
    context = {}
    context['login'] = True
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # https://stackoverflow.com/a/39316967/185820
            auth_login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.add_message(request, messages.WARNING, 'Login failed.')
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'login.html', context)


@staff_member_required
def log_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Log,
        order_by=('-created', ),
        request=request,
        search_fields=('entry', ))
    return render(request, 'log_index.html', context)


@staff_member_required
def newsletter_view(request, pk=None):
    """
    """
    context = get_page_items(
        app_settings_model=SettingsApp,
        model=Newsletter,
        pk=pk,
        request=request)
    return render(request, 'newsletter_view.html', context)


@staff_member_required
def newsletter_edit(request, pk=None):
    """
    """
    return edit(request, form_model=NewsletterForm, model=Newsletter, pk=pk)


@staff_member_required
def newsletter_index(request, pk=None):
    """
    """
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Newsletter,
        order_by=('-updated', ),
        request=request,
        search_fields=('text', ))
    return render(request, 'newsletter_index.html', context)


@login_required
def note_view(request, pk=None):
    note = get_object_or_404(Note, pk=pk)
    if not request.user.is_staff and not note.user:  # No user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    elif (not request.user.is_staff and not note.user.username ==
          request.user.username):  # Time entry user does not match user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    else:
        context = get_page_items(
            app_settings_model=SettingsApp, model=Note, pk=pk, request=request)
        return render(request, 'note_view.html', context)


@login_required
def note_edit(request, pk=None):
    return edit(
        request,
        form_model=NoteForm,
        model=Note,
        app_settings_model=SettingsApp,
        client_model=Client,
        company_model=SettingsCompany,
        pk=pk)


@staff_member_required
def note_index(request, pk=None):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Note,
        order_by=('-active', '-updated', 'tags'),
        request=request,
        search_fields=('note', 'title'))
    return render(request, 'note_index.html', context)


@staff_member_required
def plot(request):
    return get_plot(request)


@staff_member_required
def project_view(request, pk=None):
    context = get_page_items(
        app_settings_model=SettingsApp,
        model=Project,
        company_model=SettingsCompany,
        contact_model=Contact,
        estimate_model=Estimate,
        invoice_model=Invoice,
        user_model=User,
        order_by={'time': ('date', )},  # For time entries
        time_model=Time,
        pk=pk,
        request=request)
    return render(request, 'project_view.html', context)


@staff_member_required
def project_edit(request, pk=None):
    return edit(
        request,
        form_model=ProjectForm,
        model=Project,
        client_model=Client,
        pk=pk)


@staff_member_required
def project_index(request, pk=None):
    context = get_index_items(
        app_settings_model=SettingsApp,
        columns_visible={
            'project': {
                'notes': 'true',
            },
        },
        model=Project,
        order_by=(
            '-active',
            '-updated',
        ),
        request=request,
        search_fields=('id', 'name'))
    return render(request, 'project_index.html', context)


@staff_member_required
def proposal_view(request, pk=None):
    context = get_page_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        model=Proposal,
        pk=pk,
        request=request)
    return render(request, 'proposal_view.html', context)


@staff_member_required
def proposal_edit(request, pk=None):
    """
    """
    return edit(
        request,
        form_model=ProposalForm,
        model=Proposal,
        company_model=SettingsCompany,
        pk=pk)


@staff_member_required
def proposal_index(request, pk=None):
    context = get_index_items(
        app_settings_model=SettingsApp,
        model=Proposal,
        order_by=('-updated', ),
        request=request)
    return render(request, 'proposal_index.html', context)


@staff_member_required
def report_view(request, pk=None):
    context = get_page_items(
        model=Report, app_settings_model=SettingsApp, pk=pk, request=request)
    return render(request, 'report_view.html', context)


@staff_member_required
def report_edit(request, pk=None):
    return edit(
        request,
        form_model=ReportForm,
        model=Report,
        invoice_model=Invoice,
        pk=pk,
        project_model=Project)


@staff_member_required
def report_index(request):
    context = get_index_items(
        model=Report,
        app_settings_model=SettingsApp,
        order_by=('-date', ),
        request=request,
        search_fields=('id', 'name', 'gross', 'net'))
    return render(request, 'report_index.html', context)


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def service_edit(request, pk=None):
    return edit(
        request,
        form_model=ServiceForm,
        model=Service,
        company_model=SettingsCompany,
        pk=pk)


@staff_member_required
def settings_app(request):
    context = get_page_items(
        model=SettingsApp, app_settings_model=SettingsApp, request=request)
    return render(request, 'settings_app.html', context)


@staff_member_required
def settings_app_edit(request, pk=None):
    return edit(request, form_model=SettingsAppForm, model=SettingsApp, pk=1)


@staff_member_required
def settings_company(request):
    """
    """
    context = get_page_items(
        app_settings_model=SettingsApp, model=SettingsCompany, request=request)
    return render(request, 'settings_company.html', context)


@staff_member_required
def settings_company_edit(request, pk=None):
    """
    """
    return edit(
        request, form_model=SettingsCompanyForm, model=SettingsCompany, pk=1)


@staff_member_required
def settings_contract(request):
    context = get_page_items(
        model=SettingsContract,
        app_settings_model=SettingsApp,
        request=request)
    return render(request, 'settings_contract.html', context)


@staff_member_required
def settings_contract_edit(request, pk=None):
    """
    """
    return edit(
        request, form_model=SettingsContractForm, model=SettingsContract, pk=1)


@staff_member_required
def task_view(request, pk=None):
    context = get_page_items(
        model=Task, app_settings_model=SettingsApp, pk=pk, request=request)
    return render(request, 'task_view.html', context)


@staff_member_required
def task_edit(request, pk=None):
    return edit(request, form_model=TaskForm, model=Task, pk=pk)


@staff_member_required
def task_index(request):
    context = get_index_items(
        model=Task,
        app_settings_model=SettingsApp,
        order_by=(
            '-active',
            'name',
        ),
        request=request,
        search_fields=('name', ))
    return render(request, 'task_index.html', context)


@login_required
def time_view(request, pk=None):
    """
    Authenticated users can only view their own time entries unless
    they are staff.
    """
    time_entry = get_object_or_404(Time, pk=pk)
    if not request.user.is_staff and not time_entry.user:  # No user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    elif (not request.user.is_staff and not time_entry.user.username ==
          request.user.username):  # Time entry user does not match user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    else:
        context = get_page_items(
            app_settings_model=SettingsApp, model=Time, pk=pk, request=request)
        return render(request, 'time_view.html', context)


@login_required
def time_edit(request, pk=None):
    """
    Authenticated users can only edit their own time entries unless
    they are staff.
    """
    if pk is not None:
        time_entry = get_object_or_404(Time, pk=pk)
        if not request.user.is_staff and not time_entry.user:  # No user
            messages.add_message(request, messages.WARNING, message)
            return HttpResponseRedirect(reverse('home'))
        elif (not request.user.is_staff and not time_entry.user.username ==
              request.user.username):  # Time entry user does not match user
            messages.add_message(request, messages.WARNING, message)
            return HttpResponseRedirect(reverse('home'))
    if request.user.is_staff:
        time_form = AdminTimeForm
    else:
        time_form = TimeForm
    return edit(
        request,
        form_model=time_form,
        model=Time,
        invoice_model=Invoice,
        estimate_model=Estimate,
        project_model=Project,
        task_model=Task,
        time_model=Time,
        pk=pk,
    )


@staff_member_required
def time_index(request):
    search_fields = ('client__name', 'date', 'log', 'pk', 'project__name',
                     'invoice__pk', 'user__username', 'task__name')
    context = get_index_items(
        model=Time,
        app_settings_model=SettingsApp,
        columns_visible={
            'time': {
                'invoiced': 'true',
                'invoice': 'true',
                'estimate': 'true',
                'log': 'false',
            },
        },
        order_by=(
            'invoiced',
            '-updated',
        ),
        request=request,
        search_fields=search_fields)
    return render(request, 'time_index.html', context)


@login_required
def user_view(request, pk=None):
    if not request.user.pk == int(pk) and not request.user.is_staff:
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    else:
        order_by = {
            'time': ('-updated', ),
            'project': ('-updated', ),
        }
        context = get_page_items(
            app_settings_model=SettingsApp,
            contact_model=Contact,
            model=User,
            order_by=order_by,
            profile_model=Profile,
            project_model=Project,
            time_model=Time,
            pk=pk,
            request=request)
        return render(request, 'user_view.html', context)


@login_required
def user_edit(request, pk=None):
    if pk is not None:
        if has_profile(request.user):
            if not request.user.pk == int(pk) and not request.user.is_staff:
                messages.add_message(request, messages.WARNING, message)
                return HttpResponseRedirect(reverse('home'))
    if request.user.is_staff:
        profile_form = AdminProfileForm
    else:
        profile_form = ProfileForm
    return edit(
        request,
        form_model=profile_form,
        model=User,
        pk=pk,
        profile_model=Profile)


@staff_member_required
def user_index(request):
    context = get_index_items(
        app_settings_model=SettingsApp,
        company_model=SettingsCompany,
        contact_model=Contact,
        model=User,
        order_by=('-profile__active', 'last_name', 'first_name'),
        request=request)
    return render(request, 'user_index.html', context)
