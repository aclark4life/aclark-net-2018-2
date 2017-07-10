from .forms import ClientForm
from .forms import CompanyForm
from .forms import ContactForm
from .forms import ContractForm
from .forms import ContractSettingsForm
from .forms import EstimateForm
from .forms import InvoiceForm
from .forms import MailForm
from .forms import NewsletterForm
from .forms import NoteForm
from .forms import ProfileForm
from .forms import ProjectForm
from .forms import ProposalForm
from .forms import ReportForm
from .forms import SettingsForm
from .forms import ServiceForm
from .forms import TaskForm
from .models import Client
from .models import Company
from .models import Contact
from .models import Contract
from .models import ContractSettings
from .models import Estimate
from .models import Invoice
from .models import Log
from .models import Newsletter
from .models import Note
from .models import Profile
from .models import Project
from .models import Proposal
from .models import Report
from .models import Service
from .models import Settings
from .models import Testimonial
from .models import Task
from .models import Time
from .serializers import ClientSerializer
from .serializers import ProfileSerializer
from .serializers import ServiceSerializer
from .serializers import TestimonialSerializer
from .utils import add_user_to_contacts
from .utils import index_items
from .utils import create_and_send_mail
from .utils import dashboard_totals
from .utils import edit
from .utils import entries_total
from .utils import generate_doc
from .utils import get_client_city
from .utils import get_filename
from .utils import get_setting
from .utils import get_query
from .utils import get_url_name
from .utils import send_mail
from datetime import datetime
# from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
# from django.utils import timezone
from django_xhtml2pdf.utils import generate_pdf
# from faker import Faker
from io import BytesIO
from matplotlib.dates import DateFormatter
from matplotlib.dates import MonthLocator
from matplotlib.dates import date2num
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
# from pprint import pprint
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
    context = {}
    settings = Settings.get_solo()
    client = get_object_or_404(Client, pk=pk)
    contacts = Contact.objects.filter(client=client)
    contacts = contacts.order_by('-pk')
    contracts = Contract.objects.filter(client=client)
    contracts = contracts.order_by('-updated')
    projects = Project.objects.filter(client=client)
    projects = projects.order_by('-start_date')
    context['active_nav'] = 'client'
    context['edit_url'] = 'client_edit'
    context['icon_size'] = get_setting(request, settings, 'icon_size')
    context['item'] = client
    context['contacts'] = contacts
    context['contracts'] = contracts
    context['projects'] = projects
    return render(request, 'client.html', context)


@staff_member_required
def client_edit(request, pk=None):
    kwargs, url_name = get_url_name('client', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ClientForm,
        Client,
        url_name,
        'client_edit.html',
        active_nav='client',
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def client_index(request):
    search_fields = ('address', 'name')
    settings = Settings.get_solo()
    context = index_items(
        request,
        Client,
        search_fields,
        active_nav='client',
        app_settings=settings,
        edit_url='client_edit',  # Delete modal
        order_by=('-active', '-updated', 'name'),
        show_search=True)
    return render(request, 'client_index.html', context)


@staff_member_required
def company_edit(request, pk=None):
    return edit(
        request,
        CompanyForm,
        Company,
        'company',
        'company_edit.html',
        active_nav='dropdown',
        pk=1)


@staff_member_required
def company(request):
    context = {}
    company = Company.get_solo()
    context['company'] = company
    context['active_tab'] = 'company'
    context['active_nav'] = 'dropdown'
    return render(request, 'company.html', context)


@staff_member_required
def contact(request, pk=None):
    context = {}
    contact = get_object_or_404(Contact, pk=pk)
    context['active_nav'] = 'contact'
    context['edit_url'] = 'contact_edit'  # Delete modal
    context['item'] = contact
    return render(request, 'contact.html', context)


@staff_member_required
def contact_edit(request, pk=None):
    kwargs, url_name = get_url_name(
        'contact', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ContactForm,
        Contact,
        url_name,
        'contact_edit.html',
        active_nav='contact',
        client=client,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def contact_index(request):
    settings = Settings.get_solo()
    search_fields = ('first_name', 'last_name', 'email', 'notes')
    context = index_items(
        request,
        Contact,
        search_fields,
        active_nav='contact',
        app_settings=settings,
        edit_url='contact_edit',  # Delete modal
        order_by=('-active', 'first_name'),
        show_search=True)
    return render(request, 'contact_index.html', context)


@staff_member_required
def contact_mail(request, pk=None):
    context = {}
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST' and create_and_send_mail(
            request, Log, mail_form=MailForm, contact=contact, pk=pk):
        return HttpResponseRedirect(reverse('contact', kwargs={'pk': pk}))
    else:
        form = MailForm()
    context['active_nav'] = 'contact'
    context['contact'] = contact
    context['form'] = form
    return render(request, 'contact_mail.html', context)


def contact_unsubscribe(request, pk=None):
    contact = get_object_or_404(Contact, pk=pk)
    uuid = request.GET.get('id')
    if uuid == contact.uuid:
        contact.subscribed = False
        contact.save()
        messages.add_message(request, messages.SUCCESS,
                             'You have been unsubscribed!')
        log = Log(entry='%s unsubscribed.' % contact.email)
        log.save()
        return HttpResponseRedirect(reverse('home'))
    else:
        messages.add_message(request, messages.WARNING, 'Nothing to see here.')
        return HttpResponseRedirect(reverse('home'))


@staff_member_required
def contract(request, pk=None):
    """
    """
    doc = get_query(request, 'doc')
    pdf = get_query(request, 'pdf')
    company = Company.get_solo()
    context = {}
    contract = get_object_or_404(Contract, pk=pk)
    context['active_nav'] = 'contract'
    context['company'] = company
    context['edit_url'] = 'contract_edit'
    context['item'] = contract
    context['pdf'] = pdf
    # XXX In hindsight, this[1] is terrible. Maybe some OneToOne fields
    # could clean this up.
    # [1] i.e. The current implementation of time entry association with
    # estimates & invoices for the purpose of "populating" those
    # documents with line items.
    estimate = contract.statement_of_work
    if estimate:
        times_client = Time.objects.filter(
            client=estimate.client,
            estimate=None,
            project=None,
            invoiced=False,
            invoice=None)
        times_estimate = Time.objects.filter(estimate=estimate)
        times = times_client | times_estimate
        times = times.order_by('-date')
    else:
        times = None
    context['times'] = times
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        filename = get_filename(company)
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_contract.html', context=context, file_object=response)
    if doc:
        # https://stackoverflow.com/a/24122313/185820
        document = generate_doc(contract)
        filename = get_filename(company)
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
    contract_settings = ContractSettings.get_solo()
    kwargs, url_name = get_url_name(
        'contract', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ContractForm,
        Contract,
        url_name,
        'contract_edit.html',
        active_nav='contract',
        contract_settings=contract_settings,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def contract_index(request):
    """
    """
    settings = Settings.get_solo()
    search_fields = ()
    context = index_items(
        request,
        Contract,
        search_fields,
        active_nav='contract',
        app_settings=settings,
        order_by=('-created', ))
    return render(request, 'contract_index.html', context)


@staff_member_required
def contract_settings(request):
    context = {}
    contract_settings = ContractSettings.get_solo()
    fields = {}
    for field in contract_settings._meta.fields:
        if field.description == 'Text' and field.name != 'body':
            fields[field.name] = {}
            fields[field.name]['name'] = field.verbose_name
            fields[field.name]['value'] = getattr(contract_settings,
                                                  field.name)
    context['fields'] = fields
    context['active_tab'] = 'contract'
    context['active_nav'] = 'dropdown'
    return render(request, 'contract_settings.html', context)


@staff_member_required
def contract_settings_edit(request, pk=None):
    return edit(
        request,
        ContractSettingsForm,
        ContractSettings,
        'contract_settings',
        'contract_settings_edit.html',
        pk=1,
        active_nav='dropdown')


@staff_member_required
def estimate(request, pk=None):
    context = {}
    company = Company.get_solo()
    if company:
        context['company'] = company
    pdf = get_query(request, 'pdf')
    context['pdf'] = pdf
    estimate = get_object_or_404(Estimate, pk=pk)
    document_id = str(estimate.document_id)
    document_type = estimate._meta.verbose_name
    document_type_upper = document_type.upper()
    document_type_title = document_type.title()
    context['active_nav'] = 'estimate'
    context['document_type_upper'] = document_type_upper
    context['document_type_title'] = document_type_title
    context['edit_url'] = 'estimate_edit'
    context['item'] = estimate
    times_client = Time.objects.filter(
        client=estimate.client,
        estimate=None,
        project=None,
        invoiced=False,
        invoice=None)
    times_estimate = Time.objects.filter(estimate=estimate)
    times = times_client | times_estimate
    times = times.order_by('-updated')
    entries, subtotal, paid_amount, hours, amount = entries_total(times)
    context['entries'] = entries
    context['amount'] = amount
    context['paid_amount'] = paid_amount
    context['subtotal'] = subtotal
    context['hours'] = hours
    if pdf:
        company_name = ''
        if company.name:
            company_name = company.name.replace('.', '_')
            company_name = company_name.replace(', ', '_')
            company_name = company_name.upper()
        response = HttpResponse(content_type='application/pdf')
        filename = '_'.join([document_type_upper, document_id, company_name])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'estimate.html', context)


@staff_member_required
def estimate_edit(request, pk=None):
    amount = request.GET.get('amount')
    paid_amount = request.GET.get('paid_amount')
    subtotal = request.GET.get('subtotal')
    times = request.GET.get('times')
    company = Company.get_solo()
    kwargs, url_name = get_url_name(
        'estimate', page_type='index_or_edit', pk=pk)
    if times:
        estimate = get_object_or_404(Estimate, pk=pk)
        times = Time.objects.filter(pk__in=[int(i) for i in times.split(',')])
        for entry in times:
            entry.estimate = estimate
            entry.save()
    return edit(
        request,
        EstimateForm,
        Estimate,
        url_name,
        'estimate_edit.html',
        active_nav='estimate',
        amount=amount,
        company=company,
        kwargs=kwargs,
        paid_amount=paid_amount,
        pk=pk,
        subtotal=subtotal)


@staff_member_required
def estimate_index(request):
    company = Company.get_solo()
    settings = Settings.get_solo()
    search_fields = ('subject', )
    context = index_items(
        request,
        Estimate,
        search_fields,
        active_nav='estimate',
        app_settings=settings,
        edit_url='estimate_edit',  # Delete modal
        order_by=('-issue_date', ),
        show_search=True)
    context['company'] = company
    return render(request, 'estimate_index.html', context)


@staff_member_required
def estimate_mail(request, pk=None):
    estimate = get_object_or_404(Estimate, pk=pk)
    if create_and_send_mail(
            request, Log, estimate=estimate, profile_model=Profile):
        return HttpResponseRedirect(reverse('estimate', kwargs={'pk': pk}))


def home(request):
    company = Company.get_solo()
    settings = Settings.get_solo()
    gross, net, invoices_active = dashboard_totals(Invoice)
    context = {}
    invoices = Invoice.objects.filter(
        last_payment_date=None).order_by('amount')
    notes = Note.objects.filter(active=True).order_by('-updated', 'note',
                                                      'due_date', 'priority')
    projects = Project.objects.filter(active=True)
    plot_items = Report.objects.filter(active=True)
    context['edit_url'] = 'project_edit'  # Delete modal
    context['company'] = company
    context['dashboard_choices'] = get_setting(request, settings,
                                               'dashboard_choices')
    context['invoices'] = invoices
    context['icon_size'] = get_setting(request, settings, 'icon_size')
    context['gross'] = gross
    context['net'] = net
    context['notes'] = notes
    context['nav_status'] = 'active'
    context['projects'] = projects
    context['settings'] = settings
    context['plot_items'] = plot_items
    context['city_data'] = get_client_city(request)
    return render(request, 'home.html', context)


@staff_member_required
def invoice(request, pk=None):
    context = {}
    company = Company.get_solo()
    if company:
        context['company'] = company
    pdf = get_query(request, 'pdf')
    context['pdf'] = pdf
    invoice = get_object_or_404(Invoice, pk=pk)
    document_id = str(invoice.document_id)
    document_type = invoice._meta.verbose_name
    document_type_upper = document_type.upper()
    document_type_title = document_type.title()
    context['active_nav'] = 'invoice'
    context['document_type_upper'] = document_type_upper
    context['document_type_title'] = document_type_title
    context['edit_url'] = 'invoice_edit'  # Delete modal
    context['item'] = invoice
    times_project = Time.objects.filter(
        invoiced=False, project=invoice.project, estimate=None, invoice=None)
    times_invoice = Time.objects.filter(invoice=invoice)
    times = times_project | times_invoice
    times = times.order_by('-date')
    entries, subtotal, paid_amount, hours, amount = entries_total(times)
    last_payment_date = invoice.last_payment_date
    context['amount'] = amount
    context['entries'] = entries
    context['hours'] = hours
    context['invoice'] = True
    context['last_payment_date'] = last_payment_date
    context['paid_amount'] = paid_amount
    context['subtotal'] = subtotal
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        if company.name:
            company_name = company.name.replace('.', '_')
            company_name = company_name.replace(', ', '_')
            company_name = company_name.upper()
        else:
            company_name = 'COMPANY'
        filename = '_'.join([document_type_upper, document_id, company_name])
        response['Content-Disposition'] = 'filename=%s.pdf' % filename
        return generate_pdf(
            'pdf_invoice.html', context=context, file_object=response)
    else:
        return render(request, 'invoice.html', context)


@staff_member_required
def invoice_edit(request, pk=None):
    amount = request.GET.get('amount')
    paid_amount = request.GET.get('paid_amount')
    subtotal = request.GET.get('subtotal')
    times = request.GET.get('times')
    paid = request.GET.get('paid')
    company = Company.get_solo()
    project = request.GET.get('project')
    kwargs, url_name = get_url_name(
        'invoice', page_type='index_or_edit', pk=pk)
    invoice = None
    if pk:
        invoice = get_object_or_404(Invoice, pk=pk)
    if project:
        project = get_object_or_404(Project, pk=project)
    if hasattr(invoice, 'project'):
        if hasattr(invoice.project, 'client'):
            if invoice.project.client and not invoice.client:
                invoice.client = invoice.project.client
                invoice.save()
    if paid and times:
        times = Time.objects.filter(pk__in=[int(i) for i in times.split(',')])
        for entry in times:
            entry.invoiced = True
            entry.save()
    elif times:
        invoice = get_object_or_404(Invoice, pk=pk)
        times = Time.objects.filter(pk__in=[int(i) for i in times.split(',')])
        for entry in times:
            entry.invoice = invoice
            entry.save()
    return edit(
        request,
        InvoiceForm,
        Invoice,
        url_name,
        'invoice_edit.html',
        active_nav='invoice',
        amount=amount,
        company=company,
        kwargs=kwargs,
        paid_amount=paid_amount,
        paid=paid,
        pk=pk,
        project=project,
        subtotal=subtotal)


@staff_member_required
def invoice_index(request):
    company = Company.get_solo()
    settings = Settings.get_solo()
    search_fields = (
        'client__name',
        'document_id',
        'issue_date',
        'project__name',
        'subject', )
    context = index_items(
        request,
        Invoice,
        search_fields,
        active_nav='invoice',
        app_settings=settings,
        edit_url='invoice_edit',  # Delete modal
        order_by=('-issue_date', ),
        show_search=True)
    context['company'] = company
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
    settings = Settings.get_solo()
    search_fields = ('entry', )
    context = index_items(
        request,
        Log,
        search_fields,
        active_nav='dropdown',
        order_by=('-created', ),
        app_settings=settings)
    return render(request, 'log_index.html', context)


@staff_member_required
def newsletter(request, pk=None):
    """
    """
    context = {}
    newsletter = get_object_or_404(Newsletter, pk=pk)
    context['active_nav'] = 'dropdown'
    context['contacts'] = newsletter.contacts.all().order_by('first_name')
    context['edit_url'] = 'newsletter_edit'
    context['item'] = newsletter
    return render(request, 'newsletter.html', context)


@staff_member_required
def newsletter_edit(request, pk=None):
    """
    """
    kwargs, url_name = get_url_name(
        'newsletter', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        NewsletterForm,
        Newsletter,
        url_name,
        'newsletter_edit.html',
        active_nav='dropdown',
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def newsletter_index(request, pk=None):
    """
    """
    settings = Settings.get_solo()
    search_fields = ('text', )
    context = index_items(
        request,
        Newsletter,
        search_fields,
        active_nav='dropdown',
        app_settings=settings,
        order_by=('-created', ))
    return render(request, 'newsletter_index.html', context)


@staff_member_required
def newsletter_send(request, pk=None):
    """
    """
    context = {}
    newsletter = get_object_or_404(Newsletter, pk=pk)
    contacts = newsletter.contacts.all().order_by('first_name')
    for contact in contacts:
        url = reverse('contact_unsubscribe', kwargs={'pk': contact.pk})
        url = ''.join([request.get_host(), url])
        to = contact.email
        first_name = contact.first_name
        subject = newsletter.subject
        message = newsletter.text
        if send_mail(
                request,
                subject,
                message,
                to,
                url=url,
                uuid=contact.uuid,
                first_name=first_name):
            log = Log(entry='Mail sent to %s.' % to)
            log.save()
    messages.add_message(request, messages.SUCCESS, 'Batch mail sent!')
    context['active_nav'] = 'newsletter'
    context['contacts'] = contacts
    context['edit_url'] = 'newsletter_edit'
    context['item'] = newsletter
    return render(request, 'newsletter.html', context)


@staff_member_required
def note(request, pk=None):
    context = {}
    pdf = get_query(request, 'pdf')
    context['pdf'] = pdf
    note = get_object_or_404(Note, pk=pk)
    notes = Note.objects.filter(note=note)
    notes = notes.order_by('-pk')
    context['active_nav'] = 'note'
    context['edit_url'] = 'note_edit'
    context['item'] = note
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=note-%s.pdf' % pk
        return generate_pdf(
            'pdf_note.html', context=context, file_object=response)
    else:
        return render(request, 'note.html', context)


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def note_edit(request, pk=None):
    company = Company.get_solo()
    kwargs, url_name = get_url_name('note', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        NoteForm,
        Note,
        url_name,
        'note_edit.html',
        active_nav='note',
        company=company,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def note_index(request, pk=None):
    settings = Settings.get_solo()
    search_fields = ('note', )
    filters = {'hidden': False, }
    context = index_items(
        request,
        Note,
        search_fields,
        active_nav='note',
        app_settings=settings,
        filters=filters,
        order_by=('-active', '-updated', 'note', 'due_date', 'priority'),
        show_search=True)
    context['edit_url'] = 'note_edit'  # Delete modal
    return render(request, 'note_index.html', context)


@staff_member_required
def project(request, pk=None):
    settings = Settings.get_solo()
    context = {}
    project = get_object_or_404(Project, pk=pk)
    times = Time.objects.filter(
        project=project, invoiced=False).order_by('-date')
    estimates = Estimate.objects.filter(project=project)
    invoices = Invoice.objects.filter(project=project)
    context['active_nav'] = 'project'
    context['company'] = Company.get_solo()
    context['edit_url'] = 'project_edit'  # Delete modal
    context['icon_size'] = get_setting(request, settings, 'icon_size')
    context['estimates'] = estimates
    context['invoices'] = invoices
    context['item'] = project
    context['times'] = times
    return render(request, 'project.html', context)


@staff_member_required
def project_edit(request, pk=None):
    # client = request.GET.get('client')
    # client = get_object_or_404(Client, pk=client)
    # clients = Client.objects.filter(active=True)
    kwargs, url_name = get_url_name(
        'project', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ProjectForm,
        Project,
        url_name,
        'project_edit.html',
        active_nav='project',
        # client=client,
        # clients=clients,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def project_index(request, pk=None):
    settings = Settings.get_solo()
    search_fields = ('id', 'name')
    context = index_items(
        request,
        Project,
        search_fields,
        active_nav='project',
        app_settings=settings,
        edit_url='project_edit',  # Delete modal
        order_by=('-active', ),
        show_search=True)
    return render(request, 'project_index.html', context)


@staff_member_required
def proposal(request, pk=None):
    context = {}
    pdf = get_query(request, 'pdf')
    context['pdf'] = pdf
    proposal = get_object_or_404(Proposal, pk=pk)
    context['active_nav'] = 'dropdown'
    context['edit_url'] = 'proposal_edit'
    context['item'] = proposal
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=proposal-%s.pdf' % pk
        return generate_pdf(
            'pdf_proposal.html', context=context, file_object=response)
    else:
        return render(request, 'proposal.html', context)


def proposal_edit(request, pk=None):
    """
    """
    company = Company.get_solo()
    kwargs, url_name = get_url_name(
        'proposal', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ProposalForm,
        Proposal,
        url_name,
        'proposal_edit.html',
        active_nav='dropdown',
        company=company,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def proposal_index(request, pk=None):
    settings = Settings.get_solo()
    search_fields = ()
    context = index_items(
        request,
        Proposal,
        search_fields,
        active_nav='dropdown',
        app_settings=settings,
        show_search=True)
    context['edit_url'] = 'proposal_edit'  # Delete modal
    return render(request, 'proposal_index.html', context)


@staff_member_required
def report(request, pk=None):
    company = Company.get_solo()
    context = {}
    pdf = get_query(request, 'pdf')
    context['pdf'] = pdf
    report = get_object_or_404(Report, pk=pk)
    reports = Report.objects.filter(active=True)
    reports = reports.aggregate(gross=Sum(F('gross')), net=Sum(F('net')))
    context['active_nav'] = 'dropdown'
    context['company'] = company
    context['cost'] = report.gross - report.net
    context['edit_url'] = 'report_edit'  # Delete modal
    context['item'] = report
    context['reports'] = reports
    if pdf:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=report-%s.pdf' % pk
        return generate_pdf(
            'pdf_report.html', context=context, file_object=response)
    else:
        return render(request, 'report.html', context)


@staff_member_required
def report_edit(request, pk=None):
    gross, net, invoices_active = dashboard_totals(Invoice)
    kwargs, url_name = get_url_name('report', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ReportForm,
        Report,
        url_name,
        'report_edit.html',
        active_nav='dropdown',
        gross=gross,
        invoices_active=invoices_active,
        kwargs=kwargs,
        net=net,
        pk=pk)


@staff_member_required
def report_index(request):
    settings = Settings.get_solo()
    show_plot = False
    reports = Report.objects.filter(active=True)
    plot_items = reports  # Save for plotting
    reports = reports.aggregate(gross=Sum(F('gross')), net=Sum(F('net')))
    company = Company.get_solo()
    search_fields = ('id', 'name', 'gross', 'net')
    context = index_items(
        request,
        Report,
        search_fields,
        active_nav='dropdown',
        app_settings=settings,
        edit_url='report_edit',  # Delete modal
        order_by=('-date', ),
        show_search=True)
    if reports['gross'] is not None and reports['net'] is not None:
        cost = reports['gross'] - reports['net']
    else:
        reports['gross'] = 0
        reports['net'] = 0
        cost = 0
    if 'items' in context:
        if len(context['items']) > 1:
            show_plot = True
    context['reports'] = reports
    context['company'] = company
    context['cost'] = cost
    context['show_plot'] = show_plot
    context['plot_items'] = plot_items
    return render(request, 'report_index.html', context)


def report_plot(request):  # http://stackoverflow.com/a/5515994/185820
    """
    """
    values = get_query(request, 'values')
    # http://matplotlib.org/examples/api/date_demo.html
    x = [date2num(datetime.strptime(i[1], '%Y-%m-%d')) for i in values]
    y = [i[0] for i in values]
    figure = Figure()
    canvas = FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    axes.grid(True)
    axes.plot(x, y)
    axes.xaxis.set_major_locator(MonthLocator())
    axes.xaxis.set_major_formatter(DateFormatter('%m'))
    # write image data to a string buffer and get the PNG image bytes
    buf = BytesIO()
    canvas.print_png(buf)
    data = buf.getvalue()
    # write image bytes back to the browser
    return HttpResponse(data, content_type="image/png")


# https://stackoverflow.com/a/42038839/185820
@staff_member_required(login_url='login')
def service_edit(request, pk=None):
    company = Company.get_solo()
    kwargs, url_name = get_url_name('service', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ServiceForm,
        Service,
        url_name,
        'service_edit.html',
        active_nav='dropdown',
        company=company,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def settings(request):
    context = {}
    settings = Settings.get_solo()
    context['settings'] = settings
    context['active_tab'] = 'system'
    context['active_nav'] = 'dropdown'
    return render(request, 'settings.html', context)


@staff_member_required
def settings_edit(request, pk=None):
    return edit(
        request,
        SettingsForm,
        Settings,
        'settings',
        'settings_edit.html',
        active_nav='dropdown',
        pk=1)


@staff_member_required
def task(request, pk=None):
    context = {}
    task = get_object_or_404(Task, pk=pk)
    context['active_nav'] = 'task'
    context['edit_url'] = 'task_edit'  # Delete modal
    context['item'] = task
    return render(request, 'task.html', context)


@staff_member_required
def task_edit(request, pk=None):
    kwargs, url_name = get_url_name('task', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        TaskForm,
        Task,
        url_name,
        'task_edit.html',
        active_nav='task',
        pk=pk,
        kwargs=kwargs)


@staff_member_required
def task_index(request):
    settings = Settings.get_solo()
    search_fields = ('name', )
    context = index_items(
        request,
        Task,
        search_fields,
        active_nav='task',
        app_settings=settings,
        edit_url='task_edit',  # Delete modal
        order_by=('-active', ),
        show_search=True)
    return render(request, 'task_index.html', context)


@login_required
def time(request, pk=None):
    context = {}
    entry = get_object_or_404(Time, pk=pk)
    if not entry.user and not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    if entry.user:
        if (not entry.user.username == request.user.username and
                not request.user.is_staff):
            return HttpResponseRedirect(reverse('login'))
    context['active_nav'] = 'time'
    context['edit_url'] = 'entry_edit'  # Delete modal
    context['item'] = entry
    return render(request, 'time.html', context)


@login_required
def time_edit(request, pk=None):
    client = request.GET.get('client')
    project = request.GET.get('project')
    task = None
    kwargs, url_name = get_url_name('time', page_type='index_or_edit', pk=pk)
    if pk is not None:
        entry = get_object_or_404(Time, pk=pk)
        if entry.user:
            if (entry.user.username != request.user.username and
                    not request.user.is_staff):
                return HttpResponseRedirect(reverse('login'))
        else:
            if not request.user.is_staff:
                return HttpResponseRedirect(reverse('login'))
    if client:
        client = get_object_or_404(Client, pk=client)
    if project:
        project = get_object_or_404(Project, pk=project)
        if project.task:
            task = get_object_or_404(Task, pk=project.task.pk)
    projects = Project.objects.filter(team=request.user.pk)
    clients = Client.objects.filter(
        pk__in=[i.client.pk for i in projects if i.client])
    tasks = Task.objects.filter(pk__in=[i.task.pk for i in projects if i.task])
    if request.user.is_staff:
        from .forms import TimeAdminForm as TimeForm
    else:
        from .forms import TimeForm
    return edit(
        request,
        TimeForm,
        Time,
        url_name,
        'time_edit.html',
        active_nav='time',
        client=client,
        clients=clients,
        log_model=Log,
        pk=pk,
        project=project,
        projects=projects,
        task=task,
        tasks=tasks,
        kwargs=kwargs)


@login_required
def time_index(request):
    search_fields = ('client__name', 'date', 'notes', 'pk', 'project__name',
                     'invoice__document_id', 'user__username')
    settings = Settings.get_solo()
    context = index_items(
        request,
        Time,
        search_fields,
        active_nav='time',
        app_settings=settings,
        edit_url='entry_edit',  # Delete modal
        page_size=3,
        order_by=('-date', ),
        show_search=True)
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'time_index.html', context)


@login_required
def user(request, pk=None):
    company = Company.get_solo()
    contacts = Contact.objects.all()
    settings = Settings.get_solo()
    user = get_object_or_404(User, pk=pk)
    profile = Profile.objects.get_or_create(user=user)[0]
    filters = {
        'estimate': None,
        'user': user,
    }
    search_fields = ()
    context = index_items(
        request,
        Time,
        search_fields,
        active_nav='user',
        order_by=('-date', ),
        filters=filters,
        app_settings=settings)
    total_hours = context['total_hours']
    if profile.rate and total_hours:
        total_dollars = profile.rate * total_hours
    else:
        total_dollars = 0
    context['active_nav'] = 'dropdown'
    context['company'] = company
    context['edit_url'] = 'user_edit'  # Delete modal
    context['icon_size'] = get_setting(request, settings, 'icon_size')
    context['item'] = user
    context['profile'] = profile
    context['request'] = request
    context['total_dollars'] = '%.2f' % total_dollars
    context['is_contact'] = user.email in [i.email for i in contacts]
    # XXX One off to list projects, maybe refactor index_items to return
    # multiple listings e.g.
    #     projects = index_items()
    #     times = index_items()
    #     context['projects'] = projects
    #     context['times'] = times
    projects = Project.objects.filter(team__in=[user, ]).order_by('-updated')
    context['projects'] = projects
    if request.user.pk == int(pk) or request.user.is_staff:
        return render(request, 'user.html', context)
    else:
        return HttpResponseRedirect(reverse('home'))


@staff_member_required
def user_contact(request, pk=None):
    return add_user_to_contacts(request, Contact, pk=pk)


@login_required
def user_edit(request, pk=None):
    context = {}
    kwargs, url_name = get_url_name('user', page_type='index_or_edit', pk=pk)
    return edit(
        request,
        ProfileForm,
        Profile,
        url_name,
        'user_edit.html',
        active_nav='dropdown',
        context=context,
        kwargs=kwargs,
        pk=pk)


@staff_member_required
def user_index(request):
    company = Company.get_solo()
    settings = Settings.get_solo()
    # XXX FieldError at /user
    # Cannot resolve keyword 'updated' into field.
    # search_fields = ('first_name', 'last_name', 'email')
    search_fields = ()
    context = index_items(
        request,
        User,
        search_fields,
        active_nav='dropdown',
        app_settings=settings,
        order_by=('-profile__active', '-profile__updated'),
        show_search=False)
    context['company'] = company
    # Check if user is contact
    contacts = Contact.objects.all()
    items = context['items']
    for item in items:
        if item.email in [i.email for i in contacts]:
            item.is_contact = True
        else:
            item.is_contact = False
    context['items'] = items
    return render(request, 'user_index.html', context)
