from .forms import AdminProfileForm
from .forms import AdminTimeForm
from .forms import AppSettingsForm
from .forms import ClientForm
from .forms import CompanySettingsForm
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
from .models import CompanySettings
from .models import Contact
from .models import Contract
from .models import ContractSettings
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
from .utils import get_plot
from .utils import has_profile
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
def client_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings,
        contact_model=Contact,
        contract_model=Contract,
        model=Client,
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
        app_settings_model=AppSettings,
        model=Client,
        order_by=('-updated', ),
        request=request,
        search_fields=('address', 'name'),
        show_search=True)
    return render(request, 'client_index.html', context)


@staff_member_required
def contact_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings, model=Contact, pk=pk, request=request)
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
        app_settings_model=AppSettings,
        model=Contact,
        order_by=('-active', 'first_name'),
        request=request,
        search_fields=('first_name', 'last_name', 'email', 'notes', 'pk'),
        show_search=True)
    return render(request, 'contact_index.html', context)


@staff_member_required
def contract_view(request, pk=None):
    """
    """
    context = get_page_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
        model=Contract,
        pk=pk,
        time_model=Time,
        request=request)
    company = CompanySettings.get_solo()
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        filename = get_company_name(company)
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_contract.html', context=context, file_object=response)
    if context['doc']:
        # https://stackoverflow.com/a/24122313/185820
        document = generate_doc(context['item'])
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
        app_settings_model=AppSettings,
        model=Contract,
        request=request,
        order_by=('-updated', ))
    return render(request, 'contract_index.html', context)


def error(request):
    """
    """
    # return HttpResponse()
    raise


@staff_member_required
def estimate_view(request, pk=None):
    order_by = {'time': ('date', ), }
    context = get_page_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
        model=Estimate,
        order_by=order_by,
        pk=pk,
        time_model=Time,
        request=request)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        filename = '-'.join(['estimate', pk])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'estimate_view.html', context)


@staff_member_required
def estimate_edit(request, pk=None):
    return edit(
        request,
        form_model=EstimateForm,
        model=Estimate,
        company_model=CompanySettings,
        project_model=Project,
        pk=pk)


@staff_member_required
def estimate_index(request):
    company = CompanySettings.get_solo()
    context = get_index_items(
        app_settings_model=AppSettings,
        model=Estimate,
        order_by=('-issue_date', ),
        search_fields=('subject', ),
        request=request,
        show_search=True)
    context['company'] = company
    return render(request, 'estimate_index.html', context)


@staff_member_required
def file_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
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
        company_model=CompanySettings,
        pk=pk, )


@staff_member_required
def file_index(request):
    context = get_index_items(
        app_settings_model=AppSettings,
        model=File,
        order_by=('-updated', ),
        request=request, )
    return render(request, 'file_index.html', context)


def home(request):
    context = get_page_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
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
        invoice_model=Invoice,
        note_model=Note,
        order_by={
            'note': ('-updated', ),
            'project': ('-updated', ),
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
        app_settings_model=AppSettings,
        company_model=CompanySettings,
        model=Invoice,
        order_by={'time': ('date', )},  # For time entries
        pk=pk,
        request=request,
        time_model=Time)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        company_name = get_company_name(context['company'])
        model_name = context['model_name'].upper()
        filename = '_'.join([company_name, model_name, pk])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'invoice_view.html', context)


@staff_member_required
def invoice_edit(request, pk=None):
    return edit(
        request,
        form_model=InvoiceForm,
        model=Invoice,
        company_model=CompanySettings,
        project_model=Project,
        pk=pk, )


@staff_member_required
def invoice_index(request):
    search_fields = (
        'client__name',
        'issue_date',
        'project__name',
        'subject', )
    context = get_index_items(
        app_settings_model=AppSettings,
        model=Invoice,
        order_by=('-issue_date', ),
        request=request,
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
            Profile.objects.get_or_create(user=user)
            return HttpResponseRedirect(reverse('home'))
        else:
            messages.add_message(request, messages.WARNING, 'Login failed.')
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'login.html', context)


@staff_member_required
def log_index(request):
    context = get_index_items(
        app_settings_model=AppSettings,
        model=Log,
        order_by=('-updated', ),
        request=request,
        search_fields=('entry', ))
    return render(request, 'log_index.html', context)


@staff_member_required(login_url='login')
def mail(request):
    """
    """
    return edit(
        request,
        contact_model=Contact,
        estimate_model=Estimate,
        form_model=MailForm,
        note_model=Note,
        page_type='edit')


@staff_member_required
def newsletter_view(request, pk=None):
    """
    """
    context = get_page_items(
        app_settings_model=AppSettings,
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
        app_settings_model=AppSettings,
        model=Newsletter,
        order_by=('-updated', ),
        request=request,
        search_fields=('text', ))
    return render(request, 'newsletter_index.html', context)


@staff_member_required
def note_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings, model=Note, pk=pk, request=request)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=note-%s.pdf' % pk
        return generate_pdf(
            'pdf_note.html', context=context, file_object=response)
    else:
        return render(request, 'note_view.html', context)


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def note_edit(request, pk=None):
    return edit(
        request,
        form_model=NoteForm,
        model=Note,
        app_settings_model=AppSettings,
        client_model=Client,
        company_model=CompanySettings,
        pk=pk)


@staff_member_required
def note_index(request, pk=None):
    context = get_index_items(
        app_settings_model=AppSettings,
        model=Note,
        order_by=('-active', '-updated'),
        request=request,
        search_fields=('note', 'title'),
        show_search=True)
    return render(request, 'note_index.html', context)


@staff_member_required
def plot(request):
    return get_plot(request)


@staff_member_required
def project_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings,
        model=Project,
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
        app_settings_model=AppSettings,
        columns_visible={'project': {
            'notes': 'true',
        }, },
        model=Project,
        order_by=(
            '-active',
            '-updated', ),
        request=request,
        search_fields=('id', 'name'),
        show_search=True)
    return render(request, 'project_index.html', context)


@staff_member_required
def proposal_view(request, pk=None):
    context = get_page_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
        model=Proposal,
        pk=pk,
        request=request)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=proposal-%s.pdf' % pk
        return generate_pdf(
            'pdf_proposal.html', context=context, file_object=response)
    else:
        return render(request, 'proposal_view.html', context)


@staff_member_required
def proposal_edit(request, pk=None):
    """
    """
    return edit(
        request,
        form_model=ProposalForm,
        model=Proposal,
        company_model=CompanySettings,
        pk=pk)


@staff_member_required
def proposal_index(request, pk=None):
    context = get_index_items(
        app_settings_model=AppSettings,
        model=Proposal,
        order_by=('-updated', ),
        request=request,
        show_search=True)
    return render(request, 'proposal_index.html', context)


@staff_member_required
def report_view(request, pk=None):
    context = get_page_items(
        model=Report, app_settings_model=AppSettings, pk=pk, request=request)
    if context['pdf']:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=report-%s.pdf' % pk
        return generate_pdf(
            'pdf_report.html', context=context, file_object=response)
    else:
        return render(request, 'report_view.html', context)


@staff_member_required
def report_edit(request, pk=None):
    return edit(
        request,
        form_model=ReportForm,
        model=Report,
        invoice_model=Invoice,
        pk=pk)


@staff_member_required
def report_index(request):
    context = get_index_items(
        model=Report,
        app_settings_model=AppSettings,
        order_by=('-date', ),
        request=request,
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
        company_model=CompanySettings,
        pk=pk)


@staff_member_required
def settings_app(request):
    context = get_page_items(
        model=AppSettings, app_settings_model=AppSettings, request=request)
    return render(request, 'settings_app.html', context)


@staff_member_required
def settings_app_edit(request, pk=None):
    return edit(request, form_model=AppSettingsForm, model=AppSettings, pk=1)


@staff_member_required
def settings_company_edit(request, pk=None):
    return edit(
        request, form_model=CompanySettingsForm, model=CompanySettings, pk=1)


@staff_member_required
def settings_company(request):
    context = get_page_items(
        app_settings_model=AppSettings, model=CompanySettings, request=request)
    return render(request, 'settings_company.html', context)


@staff_member_required
def settings_contract(request):
    context = get_page_items(
        model=ContractSettings,
        app_settings_model=AppSettings,
        request=request)
    return render(request, 'settings_contract.html', context)


@staff_member_required
def settings_contract_edit(request, pk=None):
    return edit(
        request, form_model=ContractSettingsForm, model=ContractSettings, pk=1)


@staff_member_required
def task_view(request, pk=None):
    context = get_page_items(
        model=Task, app_settings_model=AppSettings, pk=pk, request=request)
    return render(request, 'task_view.html', context)


@staff_member_required
def task_edit(request, pk=None):
    return edit(request, form_model=TaskForm, model=Task, pk=pk)


@staff_member_required
def task_index(request):
    context = get_index_items(
        model=Task,
        app_settings_model=AppSettings,
        order_by=('-updated', ),
        request=request,
        search_fields=('name', ),
        show_search=True)
    return render(request, 'task_index.html', context)


@login_required
def time_view(request, pk=None):
    """
    Authenticated users can only view their own time entries unless
    they are staff.
    """
    time_entry = get_object_or_404(Time, pk=pk)
    message = 'Sorry, you are not allowed to view that time entry.'
    if not request.user.is_staff and not time_entry.user:  # No user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    elif (not request.user.is_staff and not time_entry.user.username ==
          request.user.username):  # Time entry user does not match user
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    else:
        context = get_page_items(
            app_settings_model=AppSettings, model=Time, pk=pk, request=request)
        return render(request, 'time_view.html', context)


@login_required
def time_edit(request, pk=None):
    """
    Authenticated users can only edit their own time entries unless
    they are staff.
    """
    if pk is not None:
        time_entry = get_object_or_404(Time, pk=pk)
        message = 'Sorry, you are not allowed to edit that time entry.'
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
        pk=pk, )


@login_required
def time_index(request):
    search_fields = ('client__name', 'date', 'log', 'pk', 'project__name',
                     'invoice__pk', 'user__username', 'task__name')
    context = get_index_items(
        model=Time,
        app_settings_model=AppSettings,
        columns_visible={
            'time': {
                'invoiced': 'true',
                'invoice': 'true',
                'estimate': 'true',
                'log': 'false',
            },
        },
        order_by=('-updated', ),
        request=request,
        search_fields=search_fields,
        show_search=True)
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'time_index.html', context)


@login_required
def user_view(request, pk=None):
    if not request.user.pk == int(pk) and not request.user.is_staff:
        message = 'Sorry, you are not allowed to view that user.'
        messages.add_message(request, messages.WARNING, message)
        return HttpResponseRedirect(reverse('home'))
    else:
        order_by = {
            'time': ('-updated', ),
            'project': ('-updated', ),
        }
        context = get_page_items(
            app_settings_model=AppSettings,
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
                message = 'Sorry, you are not allowed to edit that profile.'
                messages.add_message(request, messages.WARNING, message)
                return HttpResponseRedirect(reverse('home'))
    if request.user.is_staff:
        profile_form = AdminProfileForm
    else:
        profile_form = ProfileForm
    return edit(
        request,
        form_model=profile_form,
        model=Profile,
        pk=pk,
        user_model=User)


@staff_member_required
def user_index(request):
    context = get_index_items(
        app_settings_model=AppSettings,
        company_model=CompanySettings,
        contact_model=Contact,
        model=User,
        order_by=('-profile__active', '-profile__updated'),
        request=request,
        show_search=False)
    return render(request, 'user_index.html', context)
