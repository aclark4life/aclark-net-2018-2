from .forms import AdminProfileForm
from .forms import AdminTimeForm
from .forms import AppSettingsForm
from .forms import ClientForm
from .forms import CompanyForm
from .forms import ContactForm
from .forms import ContractForm
from .forms import ContractSettingsForm
from .forms import EstimateForm
from .forms import FileForm
from .forms import InvoiceForm
from .forms import MailForm
from .forms import NewsletterForm
from .forms import NoteForm
from .forms import ProfileForm
from .forms import ProjectForm
from .forms import ProposalForm
from .forms import ReportForm
from .forms import ServiceForm
from .forms import TaskForm
from .forms import TimeForm
from .models import AppSettings
from .models import Client
from .models import Company
from .models import Contact
from .models import Contract
from .models import ContractSettings
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
from .models import Testimonial
from .models import Task
from .models import Time
from .serializers import ClientSerializer
from .serializers import ProfileSerializer
from .serializers import ServiceSerializer
from .serializers import TestimonialSerializer
from .utils import edit
from .utils import generate_doc
from .utils import get_client_city
from .utils import get_company_name
from .utils import get_index_items
from .utils import get_page_items
from .utils import is_allowed_to_view
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
from django_xhtml2pdf.utils import generate_pdf
from io import BytesIO
from rest_framework import viewsets

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


@staff_member_required
def client(request, pk=None):
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        contact_model=Contact,
        contract_model=Contract,
        model=Client,
        pk=pk,
        project_model=Project)
    return render(request, 'client.html', context)


@staff_member_required
def client_edit(request, pk=None):
    return edit(
        request,
        form_model=ClientForm,
        model=Client,
        active_nav='client',
        pk=pk)


@staff_member_required
def client_index(request):
    context = get_index_items(
        request,
        Client,
        active_nav='client',
        app_settings_model=AppSettings,
        edit_url='client_edit',
        order_by=('-active', '-updated', 'name'),
        search_fields=('address', 'name'),
        show_search=True)
    return render(request, 'client_index.html', context)


@staff_member_required
def contact(request, pk=None):
    context = get_page_items(
        request, app_settings_model=AppSettings, model=Contact, pk=pk)
    return render(request, 'contact.html', context)


@staff_member_required
def contact_edit(request, pk=None):
    return edit(
        request,
        form_model=ContactForm,
        model=Contact,
        active_nav='contact',
        client_model=Client,
        pk=pk)


@staff_member_required
def contact_index(request):
    context = get_index_items(
        request,
        Contact,
        active_nav='contact',
        app_settings_model=AppSettings,
        edit_url='contact_edit',
        order_by=('-active', 'first_name'),
        search_fields=('first_name', 'last_name', 'email', 'notes', 'pk'),
        show_search=True)
    return render(request, 'contact_index.html', context)


@staff_member_required
def contract(request, pk=None):
    """
    """
    company = Company.get_solo()
    context = get_page_items(
        request, company_model=Company, model=Contract, pk=pk, time_model=Time)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        filename = get_company_name(company)
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_contract.html', context=context, file_object=response)
    if context['doc']:
        # https://stackoverflow.com/a/24122313/185820
        document = generate_doc(contract)
        filename = get_company_name(company)
        f = BytesIO()
        document.save(f)
        length = f.tell()
        f.seek(0)
        content_type = 'application/vnd.openxmlformats-'
        content_type += 'officedocument.wordprocessingml.document'
        response = HttpResponse(f.getvalue(), content_type=content_type)
        response['Content-Disposition'] = 'filename=%s.docx' % filename
        response['Content-Length'] = length
        return response
    else:
        return render(request, 'contract.html', context)


@staff_member_required
def contract_edit(request, pk=None):
    """
    """
    return edit(
        request,
        form_model=ContractForm,
        model=Contract,
        active_nav='contract',
        pk=pk)


@staff_member_required
def contract_index(request):
    """
    """
    context = get_index_items(
        request,
        Contract,
        active_nav='contract',
        order_by=('-updated', ),
        app_settings_model=AppSettings)
    return render(request, 'contract_index.html', context)


@staff_member_required
def estimate(request, pk=None):
    order_by = {'time': ('date', ), }
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        company_model=Company,
        model=Estimate,
        order_by=order_by,
        pk=pk,
        time_model=Time)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        filename = '-'.join(['estimate', pk])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'estimate.html', context)


@staff_member_required
def estimate_edit(request, pk=None):
    return edit(
        request,
        form_model=EstimateForm,
        model=Estimate,
        active_nav='estimate',
        company_model=Company,
        project_model=Project,
        pk=pk)


@staff_member_required
def estimate_index(request):
    company = Company.get_solo()
    context = get_index_items(
        request,
        Estimate,
        active_nav='estimate',
        app_settings_model=AppSettings,
        edit_url='estimate_edit',
        order_by=('-issue_date', ),
        search_fields=('subject', ),
        show_search=True)
    context['company'] = company
    return render(request, 'estimate_index.html', context)


@staff_member_required
def file_view(request, pk=None):
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        company_model=Company,
        model=File,
        pk=pk)
    return render(request, 'file.html', context)


@staff_member_required
def file_edit(request, pk=None):
    return edit(
        request,
        form_model=FileForm,
        model=File,
        active_nav='dropdown',
        company_model=Company,
        pk=pk, )


@staff_member_required
def file_index(request):
    context = get_index_items(
        request,
        File,
        active_nav='dropdown',
        app_settings_model=AppSettings,
        order_by=('-updated', ))
    return render(request, 'file_index.html', context)


def home(request):
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        company_model=Company,
        columns_visible={
            'note': {
                'due': 'false',
                'hidden': 'false'
            },
            'invoice': {
                'paid': 'false',
            },
        },
        invoice_model=Invoice,
        note_model=Note,
        order_by={
            'note': ('-updated', ),
            'project': ('-updated', ),
            'time': ('-updated', ),
        },
        project_model=Project,
        time_model=Time,
        report_model=Report)
    return render(request, 'home.html', context)


@staff_member_required
def invoice(request, pk=None):
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        company_model=Company,
        model=Invoice,
        order_by={'time': ('date', )},  # For time entries
        pk=pk,
        time_model=Time)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        company_name = get_company_name(context['company'])
        model_name = context['model_name'].upper()
        doc_id = context['item'].document_id or pk
        filename = '_'.join([company_name, model_name, str(doc_id)])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'invoice.html', context)


@staff_member_required
def invoice_edit(request, pk=None):
    return edit(
        request,
        form_model=InvoiceForm,
        model=Invoice,
        active_nav='invoice',
        company_model=Company,
        project_model=Project,
        pk=pk, )


@staff_member_required
def invoice_index(request):
    search_fields = (
        'client__name',
        'document_id',
        'issue_date',
        'project__name',
        'subject', )
    context = get_index_items(
        request,
        Invoice,
        active_nav='invoice',
        app_settings_model=AppSettings,
        edit_url='invoice_edit',
        order_by=('-updated', ),
        search_fields=search_fields,
        show_search=True)
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
            city_data = get_client_city(request)
            log = Log(entry='%s logged in from %s' % (user, city_data))
            log.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.add_message(request, messages.WARNING, 'Login failed.')
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'login.html', context)


@staff_member_required
def log_index(request):
    context = get_index_items(
        request,
        Log,
        active_nav='dropdown',
        app_settings_model=AppSettings,
        order_by=('-updated', ),
        search_fields=('entry', ))
    return render(request, 'log_index.html', context)


@staff_member_required(login_url='login')
def mail(request):
    """
    """
    return edit(
        request,
        contact_model=Contact,
        form_model=MailForm,
        note_model=Note,
        page_type='edit')


@staff_member_required
def newsletter(request, pk=None):
    """
    """
    context = get_page_items(
        request, app_settings_model=AppSettings, model=Newsletter, pk=pk)
    return render(request, 'newsletter.html', context)


@staff_member_required
def newsletter_edit(request, pk=None):
    """
    """
    return edit(
        request,
        form_model=NewsletterForm,
        model=Newsletter,
        active_nav='dropdown',
        pk=pk)


@staff_member_required
def newsletter_index(request, pk=None):
    """
    """
    context = get_index_items(
        request,
        Newsletter,
        active_nav='dropdown',
        app_settings_model=AppSettings,
        order_by=('-updated', ),
        search_fields=('text', ))
    return render(request, 'newsletter_index.html', context)


@staff_member_required
def note(request, pk=None):
    context = get_page_items(
        request, app_settings_model=AppSettings, model=Note, pk=pk)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=note-%s.pdf' % pk
        return generate_pdf(
            'pdf_note.html', context=context, file_object=response)
    else:
        return render(request, 'note.html', context)


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def note_edit(request, pk=None):
    return edit(
        request,
        form_model=NoteForm,
        model=Note,
        active_nav='note',
        app_settings_model=AppSettings,
        client_model=Client,
        company_model=Company,
        pk=pk)


@staff_member_required
def note_index(request, pk=None):
    context = get_index_items(
        request,
        Note,
        active_nav='note',
        app_settings_model=AppSettings,
        order_by=('-active', '-updated'),
        search_fields=('note', 'title'),
        show_search=True)
    context['edit_url'] = 'note_edit'
    return render(request, 'note_index.html', context)


@staff_member_required
def project(request, pk=None):
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        model=Project,
        contact_model=Contact,
        estimate_model=Estimate,
        invoice_model=Invoice,
        user_model=User,
        order_by={'time': ('date', )},  # For time entries
        time_model=Time,
        pk=pk)
    return render(request, 'project.html', context)


@staff_member_required
def project_edit(request, pk=None):
    return edit(
        request,
        form_model=ProjectForm,
        model=Project,
        client_model=Client,
        active_nav='project',
        pk=pk)


@staff_member_required
def project_index(request, pk=None):
    context = get_index_items(
        request,
        Project,
        active_nav='project',
        app_settings_model=AppSettings,
        columns_visible={'project': {
            'notes': 'true',
        }, },
        edit_url='project_edit',
        order_by=(
            '-active',
            '-updated', ),
        search_fields=('id', 'name'),
        show_search=True)
    return render(request, 'project_index.html', context)


@staff_member_required
def proposal(request, pk=None):
    context = get_page_items(
        request, company_model=Company, model=Proposal, pk=pk)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=proposal-%s.pdf' % pk
        return generate_pdf(
            'pdf_proposal.html', context=context, file_object=response)
    else:
        return render(request, 'proposal.html', context)


@staff_member_required
def proposal_edit(request, pk=None):
    """
    """
    return edit(
        request,
        form_model=ProposalForm,
        model=Proposal,
        active_nav='proposal',
        company_model=Company,
        pk=pk)


@staff_member_required
def proposal_index(request, pk=None):
    context = get_index_items(
        request,
        Proposal,
        active_nav='proposal',
        app_settings_model=AppSettings,
        order_by=('-updated', ),
        show_search=True)
    context['edit_url'] = 'proposal_edit'
    return render(request, 'proposal_index.html', context)


@staff_member_required
def report(request, pk=None):
    context = get_page_items(
        request, model=Report, app_settings_model=AppSettings, pk=pk)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=report-%s.pdf' % pk
        return generate_pdf(
            'pdf_report.html', context=context, file_object=response)
    else:
        return render(request, 'report.html', context)


@staff_member_required
def report_edit(request, pk=None):
    return edit(
        request,
        form_model=ReportForm,
        model=Report,
        active_nav='dropdown',
        invoice_model=Invoice,
        pk=pk)


@staff_member_required
def report_index(request):
    context = get_index_items(
        request,
        Report,
        active_nav='dropdown',
        app_settings_model=AppSettings,
        edit_url='report_edit',
        order_by=('-updated', '-active'),
        search_fields=('id', 'name', 'gross', 'net'),
        show_search=True)
    return render(request, 'report_index.html', context)


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def service_edit(request, pk=None):
    return edit(
        request,
        form_model=ServiceForm,
        model=Service,
        active_nav='dropdown',
        company_model=Company,
        pk=pk)


@staff_member_required
def settings_app(request):
    context = get_page_items(
        request, model=AppSettings, app_settings_model=AppSettings)
    return render(request, 'settings.html', context)


@staff_member_required
def settings_app_edit(request, pk=None):
    return edit(
        request,
        form_model=AppSettingsForm,
        model=AppSettings,
        active_nav='dropdown',
        pk=1)


@staff_member_required
def settings_company_edit(request, pk=None):
    return edit(
        request,
        form_model=CompanyForm,
        model=Company,
        active_nav='dropdown',
        pk=1)


@staff_member_required
def settings_company(request):
    context = get_page_items(
        request, app_settings_model=AppSettings, model=Company)
    return render(request, 'company.html', context)


@staff_member_required
def settings_contract(request):
    context = get_page_items(
        request, model=ContractSettings, app_settings_model=AppSettings)
    return render(request, 'contract_settings.html', context)


@staff_member_required
def settings_contract_edit(request, pk=None):
    return edit(
        request,
        form_model=ContractSettingsForm,
        model=ContractSettings,
        pk=1,
        active_nav='dropdown')


@staff_member_required
def task(request, pk=None):
    context = get_page_items(
        request, model=Task, app_settings_model=AppSettings, pk=pk)
    return render(request, 'task.html', context)


@staff_member_required
def task_edit(request, pk=None):
    return edit(
        request, form_model=TaskForm, model=Task, active_nav='task', pk=pk)


@staff_member_required
def task_index(request):
    context = get_index_items(
        request,
        Task,
        active_nav='task',
        app_settings_model=AppSettings,
        edit_url='task_edit',
        order_by=('-updated', ),
        search_fields=('name', ),
        show_search=True)
    return render(request, 'task_index.html', context)


@login_required
def time(request, pk=None):
    return is_allowed_to_view(
        Time,
        pk,
        request,
        app_settings_model=AppSettings,
        profile_model=Profile)


@login_required
def time_edit(request, pk=None):
    if request.user.is_staff:
        time_form = AdminTimeForm
    else:
        time_form = TimeForm
    return edit(
        request,
        form_model=time_form,
        model=Time,
        active_nav='time',
        invoice_model=Invoice,
        estimate_model=Estimate,
        project_model=Project,
        task_model=Task,
        time_model=Time,
        pk=pk, )


@login_required
def time_index(request):
    search_fields = ('client__name', 'date', 'log', 'pk', 'project__name',
                     'invoice__document_id', 'user__username')
    context = get_index_items(
        request,
        Time,
        active_nav='time',
        app_settings_model=AppSettings,
        columns_visible={
            'time': {
                'invoiced': 'true',
                'invoice': 'true',
                'estimate': 'true',
            },
        },
        edit_url='time_edit',
        order_by=('-updated', ),
        search_fields=search_fields,
        show_search=True)
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'time_index.html', context)


@login_required
def user(request, pk=None):
    order_by = {
        'time': ('-updated', ),
        'project': ('-updated', ),
    }
    context = get_page_items(
        request,
        app_settings_model=AppSettings,
        contact_model=Contact,
        model=User,
        order_by=order_by,
        profile_model=Profile,
        project_model=Project,
        time_model=Time,
        pk=pk)
    return render(request, 'user.html', context)


@login_required
def user_edit(request, pk=None):
    if request.user.is_staff:
        profile_form = AdminProfileForm
    else:
        profile_form = ProfileForm
    return edit(
        request,
        form_model=profile_form,
        model=Profile,
        active_nav='dropdown',
        pk=pk)


@staff_member_required
def user_index(request):
    context = get_index_items(
        request,
        User,
        active_nav='dropdown',
        app_settings_model=AppSettings,
        company_model=Company,
        contact_model=Contact,
        order_by=('-profile__active', '-profile__updated'),
        show_search=False)
    return render(request, 'user_index.html', context)


@staff_member_required
def plot(request):
    """
    """
