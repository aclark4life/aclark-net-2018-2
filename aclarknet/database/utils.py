from decimal import Decimal
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.gis.geoip2 import GeoIP2
from django.core.mail import send_mail as django_send_mail
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from faker import Faker
from functools import reduce
from import_export import widgets
from hashlib import md5
from io import StringIO
from lxml import etree
from operator import or_ as OR
from smtplib import SMTPSenderRefused

URL_NAMES = {
    'client': ('client', 'client_edit', 'client_index'),
    'contact': ('contact', 'contact_edit', 'contact_index'),
    'contract': ('contract', 'contract_edit', 'contract_index'),
    'Company': ('company', 'company_edit', ''),
    'estimate': ('estimate', 'estimate_edit', 'estimate_index'),
    'file': ('file', 'file_edit', 'file_index'),
    'invoice': ('invoice', 'invoice_edit', 'invoice_index'),
    'newsletter': ('newsletter', 'newsletter_edit', 'newsletter_index'),
    'note': ('note', 'note_edit', 'note_index'),
    'profile': ('user', 'user_edit', 'user_index'),
    'project': ('project', 'project_edit', 'project_index'),
    'proposal': ('proposal', 'proposal_edit', 'proposal_index'),
    'report': ('report', 'report_edit', 'report_index'),
    'service': ('company', 'service_edit', ''),
    'app settings': ('settings', 'settings_edit', ''),
    'task': ('task', 'task_edit', 'task_index'),
    'time': ('time_entry', 'time_edit', 'time_index'),
    'user': ('user', 'user_edit', 'user_index'),
}


class BooleanWidget(widgets.Widget):
    """
    Convert strings to boolean values
    """

    def clean(self, value):
        if value == 'Yes':
            return True
        else:
            return False


class DecimalWidget(widgets.Widget):
    """
    Convert strings to decimal values
    """

    def clean(self, value):
        if value:
            return Decimal(value.replace(',', ''))
        else:
            return Decimal(0)


class UserWidget(widgets.Widget):
    """
    """

    def clean(self, value):
        return value


def add_user_to_contacts(request, model, pk=None):
    """
    """
    if request.method == 'POST':
        if pk is None:
            return HttpResponseRedirect(reverse('user_index'))
        else:
            user = get_object_or_404(User, pk=pk)
            if not user.email or not user.first_name or not user.last_name:
                messages.add_message(request, messages.WARNING,
                                     'No email no contact!')
                return HttpResponseRedirect(reverse('user_index'))
            contact = model.objects.filter(email=user.email)
            if contact:
                contact = contact[0].email
                messages.add_message(request, messages.WARNING,
                                     'Found duplicate: %s!' % contact)
                return HttpResponseRedirect(reverse('user_index'))
            contact = model(
                email=user.email,
                active=True,
                first_name=user.first_name,
                last_name=user.last_name)
            contact.save()
            messages.add_message(request, messages.INFO,
                                 'User added to contacts!')
            return HttpResponseRedirect(reverse('contact_index'))


def check_boxes(obj, checkbox_active, checkbox_subscribed, refer,
                app_settings_model):
    if checkbox_active == 'on' or checkbox_active == 'off':
        if checkbox_active == 'on':
            obj.active = True
        else:
            obj.active = False
        # Special case for note
        if obj._meta.verbose_name == 'note' and app_settings_model:
            app_settings = app_settings_model.get_solo()
            if app_settings.auto_hide_notes:
                obj.hidden = True
        obj.save()
        return HttpResponseRedirect(refer)
    if checkbox_subscribed == 'on' or checkbox_subscribed == 'off':
        if checkbox_subscribed == 'on':
            obj.subscribed = True
        else:
            obj.subscribed = False
        obj.save()
        return HttpResponseRedirect(refer)


def create_and_send_mail(request,
                         log_model,
                         mail_form=None,
                         contact=None,
                         estimate=None,
                         profile_model=None,
                         pk=None):
    """
    """
    if contact:
        form = mail_form(request.POST)
        if form.is_valid():
            test = form.cleaned_data['test']
            if test:
                fake = Faker()
                subject = fake.text()
                message = fake.text()
            else:
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
            url = reverse('contact_unsubscribe', kwargs={'pk': pk})
            url = ''.join([request.get_host(), url])
            to = contact.email
            first_name = contact.first_name
            if send_mail(
                    request,
                    subject,
                    message,
                    to,
                    url=url,
                    uuid=contact.uuid,
                    first_name=first_name):
                messages.add_message(request, messages.SUCCESS, 'Mail sent!')
                log = log_model(entry='Mail sent to %s.' % to)
                log.save()
                return True
    if estimate:
        notes = '<ol><li>'
        counter = 0
        hours = 0
        rate = estimate.project.task.rate
        start_date = estimate.project.start_date.strftime('%m/%d/%Y')
        end_date = estimate.project.end_date.strftime('%m/%d/%Y')
        subject = estimate.subject
        now = timezone.datetime.now().strftime('%m/%d/%Y at %H:%M:%S')
        for entry in estimate.time_set.all():
            if counter != 0:
                notes += '</li><li>%s <strong>%s hours</strong>.' % (
                    entry.log, entry.hours)
            else:
                notes += '%s <strong>%s hours</strong>.' % (entry.log,
                                                            entry.hours)
            counter += 1
            hours += entry.hours
        notes += '</li></ol>'
        cost = hours * rate
        url = reverse('estimate', kwargs={'pk': estimate.pk})
        url = ''.join([request.get_host(), url])
        message = ''.join([
            '<h1 style="text-align: center">Statement of Work</h1><h2>%s '
            'total hours of %s at rate of $%s/hour for %s = $%.2f from %s'
            ' to %s.</h2>' %
            (hours, estimate.subject, rate, estimate.client.name, cost,
             start_date, end_date), notes
        ])
        profiles = profile_model.objects.filter(app_admin=True)
        for profile in profiles:
            email = profile.user.email
            if send_mail(
                    request,
                    'Statement of Work for %s sent on %s.' % (subject, now),
                    message,
                    email,
                    url=url):
                log = log_model(
                    entry='Statement of Work for %s sent on %s to %s.' %
                    (subject, now, email))
                log.save()
        messages.add_message(request, messages.SUCCESS, 'Sent to app_admins.')
        return True
    return False


def daily_burn(project):
    try:
        days = (project.end_date - project.start_date).days
        hours = project.budget
        burn = hours / days
        return '%.2f' % burn
    except (TypeError, ZeroDivisionError):
        return ''


def edit(
        request,
        form_model,
        model,
        url_name,
        template_name,
        active_nav=None,
        app_settings_model=None,
        client_model=None,
        company_model=None,
        company_note=None,
        estimate_model=None,
        invoice_model=None,
        project_model=None,
        task_model=None,
        time_model=None,
        pk=None, ):
    context = {}
    obj = None
    if pk is None:
        form = form_model()
    else:
        obj = get_object_or_404(model, pk=pk)
        form = form_model(instance=obj)
    if request.method == 'POST':
        refer = request.META['HTTP_REFERER']
        if pk is None:
            form = form_model(request.POST)
        else:
            checkbox_active = request.POST.get('checkbox')
            checkbox_subscribed = request.POST.get('checkbox-subscribed')
            copy = request.POST.get('copy')
            delete = request.POST.get('delete')
            # Copy or delete
            if copy:
                # return obj_copy(obj, url_name)
                return obj_copy(obj)
            if delete:
                # return obj_delete(obj, company, request=request)
                return obj_delete(obj)
            # Check boxes
            if (checkbox_active == 'on' or checkbox_active == 'off' or
                    checkbox_subscribed == 'on' or
                    checkbox_subscribed == 'off'):
                return check_boxes(obj, checkbox_active, checkbox_subscribed,
                                   refer, app_settings_model)
            form = form_model(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            set_relationship(
                obj,
                request,
                client_model=client_model,
                estimate_model=estimate_model,
                invoice_model=invoice_model,
                project_model=project_model)
            return obj_edit(obj, pk=pk)
    context['active_nav'] = active_nav
    context['form'] = form
    context['item'] = obj
    context['pk'] = pk
    if company_model:
        company = company_model.get_solo()
        context['company'] = company
    if invoice_model:  # Dashboard totals for reporting
        gross, net = get_invoice_totals(invoice_model)
        context['gross'] = gross
        context['net'] = net
    return render(request, template_name, context)


def generate_doc(contract):
    """
    https://stackoverflow.com/a/24122313/185820
    """
    document = Document()
    # Head
    task = ''
    if contract.task:
        task = contract.task
    title = document.add_heading(
        'ACLARK.NET, LLC %s AGREEMENT PREPARED FOR:' % task, level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if contract.client:
        client_name = document.add_heading(contract.client.name, level=1)
        client_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        client_address = document.add_heading(contract.client.address, level=1)
        client_address.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parser = etree.HTMLParser()  # http://lxml.de/parsing.html
    tree = etree.parse(StringIO(contract.body), parser)
    # Body
    for element in tree.iter():
        if element.tag == 'h2':
            document.add_heading(element.text, level=2)
        elif element.tag == 'p':
            document.add_paragraph(element.text)
    return document


def get_active_kwarg(model, active=False, user=None):
    """
    Kwarg for "active" varies by type
    """
    kwargs = {}
    if model._meta.verbose_name == 'estimate':
        # Unaccepted invoices are "active"
        if active:
            kwargs['accepted_date'] = None
    elif model._meta.verbose_name == 'invoice':
        # Unpaid invoices are "active"
        if active:
            kwargs['last_payment_date'] = None
    elif model._meta.verbose_name == 'time':
        # Only staff can see all items
        if not user.is_staff:
            kwargs['user'] = user
        # Uninvoiced times are "active"
        kwargs['invoiced'] = not (active)
        # Estimated times are never "active"
        kwargs['estimate'] = None
    elif model._meta.verbose_name == 'user':
        # Use related model's active field
        kwargs['profile__active'] = active
    else:
        # All other models check active field
        kwargs['active'] = active
    return kwargs


def get_client_city(request):
    ip_address = get_client_ip(request)
    geo = GeoIP2()
    if ip_address:
        return geo.city(ip_address)


# https://stackoverflow.com/a/4581997/185820
def get_client_ip(request):
    return request.META.get('HTTP_X_REAL_IP')


def get_company_name(company):
    if company.name:
        company_name = company.name.replace('.', '_')
        company_name = company_name.replace(', ', '_')
        company_name = company_name.upper()
        return company_name
    else:
        fake = Faker()
        return fake.text()


def get_invoice_totals(model):
    invoices = model.objects.filter(last_payment_date=None)
    total = 0
    for invoice in invoices:
        if invoice.amount:
            total += invoice.amount
    return total, total


def get_line_total(entries, entry):
    line_total = 0
    return line_total


def get_query(request, query):
    """
    """
    # Special handling for some query strings
    if query == 'paginated':
        paginated = request.GET.get('paginated')
        if paginated == u'false':
            return False
        else:
            return True
    elif query == 'search' and request.method == 'POST':
        return request.POST.get('search', '')
    elif query == 'values':
        values = request.GET.get('values')
        if values:
            values = values.split(' ')
        else:
            values = []
        values = [i.split(',') for i in values]
        return values
    else:  # Normal handling
        return request.GET.get(query, '')


def get_search_results(model,
                       search_fields,
                       search,
                       active_nav='',
                       app_settings_model=None,
                       edit_url='',
                       request=None):
    context = {}
    query = []
    for field in search_fields:
        query.append(Q(**{field + '__icontains': search}))
    items = model.objects.filter(reduce(OR, query))
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['items'] = items
    context['show_search'] = True
    return context


def get_setting(request, app_settings_model, setting, page_size=None):
    """
    Allow user to override global setting
    """
    if not request.user.is_authenticated:
        return
    override = user_pref = None
    app_settings = app_settings_model.get_solo()
    if setting == 'icon_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.icon_size
        if user_pref:
            return user_pref
        else:
            return app_settings.icon_size
    if setting == 'page_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.page_size
        if user_pref:
            return user_pref
        elif page_size:  # View's page_size preference
            return page_size
        else:
            return app_settings.page_size
    if setting == 'dashboard_choices':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.dashboard_choices
            override = request.user.profile.override_dashboard
        if override:
            return user_pref
        else:
            return app_settings.dashboard_choices


def get_template_and_url_names(verbose_name, page_type=None):
    """
    """
    if page_type == 'view':
        url_name = URL_NAMES[verbose_name][0]
        template_name = '%s.html' % url_name
        return template_name, url_name
    elif page_type == 'edit':
        url_name = URL_NAMES[verbose_name][1]
        template_name = '%s.html' % url_name
        return template_name, url_name
    elif page_type == 'index':
        url_name = URL_NAMES[verbose_name][2]
        return url_name


def get_times_for_invoice(invoice, time_model):
    times_project = time_model.objects.filter(
        invoiced=False, project=invoice.project, estimate=None, invoice=None)
    times_invoice = time_model.objects.filter(invoice=invoice)
    times = times_project | times_invoice
    return times


def gravatar_url(email):
    """
    MD5 hash of email address for use with Gravatar
    """
    return django_settings.GRAVATAR_URL % md5(email.lower()).hexdigest()


def get_amount(times, invoice=None):
    amount = 0
    total = 0
    for entry in times:
        if entry.task:
            amount = entry.task.rate * entry.hours
        entry.amount = '%.2f' % amount
        total += amount
    if invoice:
        invoice.amount = '%.2f' % total
        invoice.save()
    return times


def get_index_items(request,
                    model,
                    app_settings_model=None,
                    active_nav=None,
                    company_model=None,
                    contact_model=None,
                    edit_url=None,
                    order_by=None,
                    page_size=None,
                    search_fields=None,
                    show_search=False):
    """
    """
    context = {}
    if company_model:
        company = company_model.get_solo()
        context['company'] = company
    page = get_query(request, 'page')
    paginated = get_query(request, 'paginated')
    search = get_query(request, 'search')
    # Search is easy
    if request.method == 'POST':
        if search == u'':  # Empty search returns none
            context['active_nav'] = active_nav
            context['show_search'] = True
            return context
        else:
            return get_search_results(
                model,
                search_fields,
                search,
                active_nav=active_nav,
                app_settings_model=app_settings_model,
                edit_url=edit_url,
                request=request)
    # Not a search
    items = model.objects.all()
    # Order items (http://stackoverflow.com/a/20257999/185820)
    if order_by is not None:
        items = items.order_by(*order_by)
    # Calculate total hours
    if model._meta.verbose_name == 'time':
        total_hours = items.aggregate(hours=Sum(F('hours')))
        total_hours = total_hours['hours']
        context['total_hours'] = total_hours
    # Calculate cost per report
    if model._meta.verbose_name == 'report':
        for item in items:
            cost = item.gross - item.net
            item.cost = cost
            item.save()
    # Check if user is contact
    if model._meta.verbose_name == 'user':
        contacts = contact_model.objects.all()
        for item in items:
            if item.email in [i.email for i in contacts]:
                item.is_contact = True
            else:
                item.is_contact = False
    # Don't show items to anon
    if not request.user.is_authenticated:
        items = []
    # Paginate if paginated
    if paginated:
        page_size = get_setting(
            request, app_settings_model, 'page_size', page_size=page_size)
        items = paginate(items, page, page_size)
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['items'] = items
    context['page'] = page
    context['paginated'] = paginated
    context['show_search'] = show_search
    # Provide number of active notes to note_index
    if model._meta.verbose_name == 'note':
        context['note_stats'] = get_note_stats(model)
    return context


def get_note_stats(note_model):
    note_stats = {}
    active = len(note_model.objects.filter(active=True))
    hidden = len(note_model.objects.filter(hidden=True))
    inactive = len(note_model.objects.filter(active=False))
    total = len(note_model.objects.all())
    not_hidden = inactive - hidden
    note_stats['active_note_count'] = active
    note_stats['hidden_note_count'] = hidden
    note_stats['inactive_note_count'] = inactive
    note_stats['total_note_count'] = total
    note_stats['not_hidden_count'] = not_hidden
    return note_stats


def get_page_items(request,
                   app_settings_model=None,
                   company_model=None,
                   contact_model=None,
                   contract_model=None,
                   estimate_model=None,
                   invoice_model=None,
                   model=None,
                   note_model=None,
                   profile_model=None,
                   project_model=None,
                   report_model=None,
                   order_by=None,
                   pk=None,
                   time_model=None):
    context = {}
    if company_model:
        company = company_model.get_solo()
        context['company'] = company
    if model:
        if model._meta.verbose_name == 'client':
            client = get_object_or_404(model, pk=pk)
            contacts = contact_model.objects.filter(client=client)
            contracts = contract_model.objects.filter(client=client)
            projects = project_model.objects.filter(client=client)
            context['active_nav'] = 'client'
            context['contacts'] = contacts
            context['contracts'] = contracts
            context['edit_url'] = 'client_edit'
            context['icon_size'] = get_setting(request, app_settings_model,
                                               'icon_size')
            context['item'] = client
            context['notes'] = client.note.all()
            context['projects'] = projects
        elif model._meta.verbose_name == 'contract':
            contract = get_object_or_404(model, pk=pk)
            doc = get_query(request, 'doc')
            estimate = contract.statement_of_work
            pdf = get_query(request, 'pdf')
            if estimate:
                times_client = time_model.objects.filter(
                    client=estimate.client,
                    estimate=None,
                    project=None,
                    invoiced=False,
                    invoice=None)
                times_estimate = time_model.objects.filter(estimate=estimate)
                times = times_client | times_estimate
            else:
                times = None
            context['active_nav'] = 'contract'
            context['doc'] = doc
            context['edit_url'] = 'contract_edit'
            context['item'] = contract
            context['pdf'] = pdf
            context['times'] = times
        elif model._meta.verbose_name == 'estimate':
            estimate = get_object_or_404(model, pk=pk)
            document_type = estimate._meta.verbose_name
            document_type_upper = document_type.upper()
            document_type_title = document_type.title()
            pdf = get_query(request, 'pdf')
            times_client = time_model.objects.filter(
                client=estimate.client,
                estimate=None,
                project=None,
                invoiced=False,
                invoice=None)
            times_estimate = time_model.objects.filter(estimate=estimate)
            times = times_client | times_estimate
            times = get_amount(times)
            context['active_nav'] = 'estimate'
            context['document_type_upper'] = document_type_upper
            context['document_type_title'] = document_type_title
            context['entries'] = times
            context['edit_url'] = 'estimate_edit'
            context['item'] = estimate
            context['pdf'] = pdf
        if model._meta.verbose_name == 'file':
            file_obj = get_object_or_404(model, pk=pk)
            context['active_nav'] = 'dropdown'
            context['edit_url'] = 'file_edit'
            context['icon_size'] = get_setting(request, app_settings_model,
                                               'icon_size')
            context['item'] = file_obj
        elif model._meta.verbose_name == 'invoice':
            invoice = get_object_or_404(model, pk=pk)
            document_type = invoice._meta.verbose_name
            document_type_upper = document_type.upper()
            document_type_title = document_type.title()
            times = get_times_for_invoice(invoice, time_model)
            times = times.order_by(*order_by['time'])
            times = get_amount(times, invoice=invoice)
            last_payment_date = invoice.last_payment_date
            pdf = get_query(request, 'pdf')
            context['active_nav'] = 'invoice'
            context['document_type_upper'] = document_type_upper
            context['document_type_title'] = document_type_title
            context['edit_url'] = 'invoice_edit'  # Delete modal
            context['entries'] = times
            context['item'] = invoice
            context['invoice'] = True
            context['last_payment_date'] = last_payment_date
            context['pdf'] = pdf
        elif model._meta.verbose_name == 'project':
            project = get_object_or_404(model, pk=pk)
            invoices = project.invoice_set.all()
            invoice = times = None
            if len(invoices) > 0:
                invoice = invoices[0]
                times = get_times_for_invoice(invoice, time_model)
                times = times.order_by(*order_by['time'])
            estimates = estimate_model.objects.filter(
                project=project, accepted_date=None)
            invoices = invoice_model.objects.filter(
                project=project, last_payment_date=None)
            context['active_nav'] = 'project'
            context['edit_url'] = 'project_edit'  # Delete modal
            context['entries'] = times
            context['icon_size'] = get_setting(request, app_settings_model,
                                               'icon_size')
            context['estimates'] = estimates
            context['invoices'] = invoices
            context['item'] = project
            context['times'] = times
        elif model._meta.verbose_name == 'proposal':
            proposal = get_object_or_404(model, pk=pk)
            pdf = get_query(request, 'pdf')
            context['active_nav'] = 'dropdown'
            context['edit_url'] = 'proposal_edit'  # Delete modal
            context['item'] = proposal
            context['pdf'] = pdf
        elif model._meta.verbose_name == 'user':
            user = get_object_or_404(model, pk=pk)
            filters = {
                'estimate': None,
                'invoiced': False,
                'user': user,
            }
            projects = project_model.objects.filter(
                team__in=[user, ], active=True)
            projects = projects.order_by(*order_by['project'])
            times = time_model.objects.filter(**filters)
            times = times.order_by(*order_by['time'])
            contacts = contact_model.objects.all()
            context['active_nav'] = 'dropdown'
            context['is_contact'] = user.email in [i.email for i in contacts]
            context['item'] = user
            context['profile'] = profile_model.objects.get_or_create(
                user=user)[0]
            context['projects'] = projects
            context['times'] = times
    else:  # home
        invoices = invoice_model.objects.filter(last_payment_date=None)
        notes = note_model.objects.filter(active=True)
        notes = notes.order_by(*order_by['note'])
        projects = project_model.objects.filter(active=True, hidden=False)
        projects = projects.order_by(*order_by['project'])
        plot_items = report_model.objects.filter(active=True)
        gross, net = get_invoice_totals(invoice_model)
        context['note_stats'] = get_note_stats(note_model)
        context['city_data'] = get_client_city(request)
        context['dashboard_choices'] = get_setting(request, app_settings_model,
                                                   'dashboard_choices')
        context['gross'] = gross
        context['invoices'] = invoices
        context['icon_size'] = get_setting(request, app_settings_model,
                                           'icon_size')
        context['nav_status'] = 'active'
        context['net'] = net
        context['notes'] = notes
        context['plot_items'] = plot_items
        context['projects'] = projects
    return context


def last_month():
    """
    Returns last day of last month
    """
    first = timezone.now().replace(day=1)
    return first - timezone.timedelta(days=1)


def obj_copy(obj):
    dup = obj
    dup.pk = None
    dup.save()
    kwargs = {}
    kwargs['pk'] = dup.pk
    template_name, url_name = get_template_and_url_names(
        obj._meta.verbose_name, page_type='edit')
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def obj_delete(obj):
    url_name = get_template_and_url_names(
        obj._meta.verbose_name, page_type='index')  # Redir to index
    obj.delete()
    return HttpResponseRedirect(reverse(url_name))


def obj_edit(obj, pk=None):
    verbose_name = obj._meta.verbose_name
    template_name, url_name = get_template_and_url_names(
        verbose_name, page_type='view')  # Redir to view
    # New or existing object
    kwargs = {}
    if pk:  # Existing
        if verbose_name == 'Company':  # Special case for company
            return HttpResponseRedirect(reverse(url_name))
        if verbose_name == 'app settings':  # Special case for settings
            return HttpResponseRedirect(reverse(url_name))
        kwargs['pk'] = pk
    else:  # New
        kwargs['pk'] = obj.pk
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def paginate(items, page, page_size):
    """
    """
    paginator = Paginator(items, page_size, orphans=5)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items


def send_mail(request,
              subject,
              message,
              to,
              url=None,
              uuid=None,
              first_name=None):
    recipients = []
    sender = django_settings.EMAIL_FROM
    recipients.append(to)
    # http://stackoverflow.com/a/28476681/185820
    if first_name:
        username = first_name
    else:
        username = to
    html_message = render_to_string('cerberus-fluid.html', {
        'username': username,
        'message': message,
        'url': url,
        'uuid': uuid,
    })
    try:
        django_send_mail(
            subject,
            message,
            sender,
            recipients,
            fail_silently=False,
            html_message=html_message)
        return True
    except SMTPSenderRefused:
        messages.add_message(request, messages.WARNING, 'SMTPSenderRefused!')
        return False


def set_relationship(
        obj,
        request,
        client_model=None,
        company_model=None,
        estimate_model=None,
        invoice_model=None,
        project_model=None):
    verbose_name = obj._meta.verbose_name
    if verbose_name == 'contact':
        query_string_client = get_query(request, 'client')
        if query_string_client:
            client = get_object_or_404(client_model, pk=query_string_client)
            obj.client.add(client)
            obj.save()
            return True
    elif verbose_name == 'note':
        query_string_client = get_query(request, 'client')
        query_string_company = get_query(request, 'company')
        if query_string_client:
            client = get_object_or_404(client_model, pk=query_string_client)
            client.note.add(obj)
            client.save()
            return True
        elif query_string_company:
            company = company_model.get_solo()
            company.note.add(obj)
            company.save()
    elif verbose_name == 'time':
        query_string_invoices = get_query(request, 'invoice')
        query_string_project = get_query(request, 'project')
        if query_string_invoices:
            invoices = query_string_invoices.split(',')
            if len(invoices) > 1:
                return False
            else:
                invoice = invoices[0]
                invoice = get_object_or_404(invoice_model, pk=invoice)
                obj.invoice = invoice
                obj.save()
        if query_string_project:
            project = get_object_or_404(project_model, pk=query_string_project)
            obj.task = project.task
            obj.save()
        return True
