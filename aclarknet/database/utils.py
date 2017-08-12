from collections import OrderedDict
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

ITEMS_NAME = {
    'client': 'clients',
    'contact': 'contacts',
    'contract': 'contracts',
    'estimate': 'estimates',
    'file': 'files',
    'invoice': 'invoices',
    'log': 'logs',
    'newsletter': 'newsletters',
    'note': 'notes',
    'profile': 'profiles',
    'project': 'projects',
    'proposal': 'proposals',
    'report': 'reports',
    'service': 'services',
    'task': 'tasks',
    'time': 'times',
    'user': 'users',
}

URL_NAMES = {
    'app settings': ('settings_app', 'settings_app_edit', ''),
    'client': ('client', 'client_edit', 'client_index'),
    'contact': ('contact', 'contact_edit', 'contact_index'),
    'contract': ('contract', 'contract_edit', 'contract_index'),
    'contract settings': ('settings_contract', 'settings_contract_edit', ''),
    'Company': ('settings_company', 'settings_company_edit', ''),
    'estimate': ('estimate', 'estimate_edit', 'estimate_index'),
    'file': ('file', 'file_edit', 'file_index'),
    'invoice': ('invoice', 'invoice_edit', 'invoice_index'),
    'log': ('log', 'log_edit', 'log_index'),
    'newsletter': ('newsletter', 'newsletter_edit', 'newsletter_index'),
    'note': ('note', 'note_edit', 'note_index'),
    'profile': ('user', 'user_edit', 'user_index'),
    'project': ('project', 'project_edit', 'project_index'),
    'proposal': ('proposal', 'proposal_edit', 'proposal_index'),
    'report': ('report', 'report_edit', 'report_index'),
    'service': ('company', 'service_edit', ''),
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
            messages.add_message(request, messages.SUCCESS,
                                 'User added to contacts!')
            if hasattr(user, 'profile'):
                user.profile.is_contact = True
                user.save()
            return HttpResponseRedirect(reverse('contact_index'))


def send_mail(subject, message, sender, recipients, **kwargs):
    message = kwargs['message']
    request = kwargs['request']
    user = kwargs['user']
    url = kwargs['url']
    html_message = get_html_message(message, url, user)
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


def set_check_boxes(obj, cb_query, refer, app_settings_model):
    model_name = obj._meta.verbose_name
    if cb_query['active'] == 'on' or cb_query['active'] == 'off':  # Active
        if cb_query['active'] == 'on':
            obj.active = True
        else:
            obj.active = False
        # Auto-hide notes
        if model_name == 'note' and app_settings_model:
            app_settings = app_settings_model.get_solo()
            if app_settings.auto_hide_notes:
                obj.hidden = True
    elif cb_query['subscribe'] == 'on' or cb_query[
            'subscribe'] == 'off':  # Subscribe
        if cb_query['active'] == 'on':
            obj.subscribed = True
        else:
            obj.subscribed = False
    obj.save()
    return HttpResponseRedirect(refer)


def daily_burn(project):
    try:
        days = (project.end_date - project.start_date).days
        hours = project.budget
        burn = hours / days
        return '%.2f' % burn
    except (TypeError, ZeroDivisionError):
        return ''


def edit(request, **kwargs):
    context = {}
    obj = None
    active_nav = kwargs.get('active_nav')
    app_settings_model = kwargs.get('app_settings_model')
    client_model = kwargs.get('client_model')
    company_model = kwargs.get('company_model')
    estimate_model = kwargs.get('estimate_model')
    form_model = kwargs.get('form_model')
    invoice_model = kwargs.get('invoice_model')
    model = kwargs.get('model')
    pk = kwargs.get('pk')
    project_model = kwargs.get('project_model')
    task_model = kwargs.get('task_model')
    time_model = kwargs.get('time_model')
    model_name = model._meta.verbose_name
    if pk is None:
        form = get_form(
            request,
            form_model,
            model,
            client_model=client_model,
            company_model=company_model,
            estimate_model=estimate_model,
            invoice_model=invoice_model,
            project_model=project_model,
            task_model=task_model,
            time_model=time_model)
    else:
        obj = get_object_or_404(model, pk=pk)
        if model_name == 'note':  # Populate form with tags already set
            form = form_model(initial={'tags': obj.tags.all()}, instance=obj)
        else:
            form = form_model(instance=obj)
    if request.method == 'POST':
        refer = request.META['HTTP_REFERER']
        if pk is None:
            form = form_model(request.POST)
        else:
            # Copy or delete
            copy = request.POST.get('copy')
            delete = request.POST.get('delete')
            if copy:
                return obj_copy(obj)
            if delete:
                return obj_remove(obj)
            # Check boxes
            cb_query = get_query(request, 'checkbox')
            if cb_query['condition']:
                return set_check_boxes(obj, cb_query, refer,
                                       app_settings_model)
            form = form_model(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            set_relationship(
                obj,
                request,
                client_model=client_model,
                company_model=company_model,
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
    template_name = get_template_and_url_names(model_name, page_type='edit')
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
    model_name = model._meta.verbose_name
    if model_name == 'estimate':
        # Unaccepted invoices are "active"
        if active:
            kwargs['accepted_date'] = None
    elif model_name == 'invoice':
        # Unpaid invoices are "active"
        if active:
            kwargs['last_payment_date'] = None
    elif model_name == 'time':
        # Only staff can see all items
        if not user.is_staff:
            kwargs['user'] = user
        # Uninvoiced times are "active"
        kwargs['invoiced'] = not (active)
        # Estimated times are never "active"
        kwargs['estimate'] = None
    elif model_name == 'user':
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
        company_name = company.name
    else:
        fake = Faker()
        company_name = fake.text()
    company_name = company.name.replace('.', '_')
    company_name = company_name.replace(', ', '_')
    company_name = company_name.upper()
    return company_name


def get_fields(items):
    for item in items:
        fields = item._meta._get_fields()
        item.fields = OrderedDict()
        for field in fields:
            if not field.is_relation:
                item.fields[field.name] = getattr(item, field.name)
    return items


def get_form(request, form_model, model, **kwargs):
    model_name = model._meta.verbose_name
    if model_name == 'report':  # Populate report with gross, net.
        invoice_model = kwargs['invoice_model']
        gross, net = get_invoice_totals(invoice_model)
        obj = model(gross=gross, net=net)
        form = form_model(instance=obj)
    else:
        form = form_model()
    return form


def get_html_message(message, url, user):
    # http://stackoverflow.com/a/28476681/185820
    return render_to_string('cerberus-fluid.html', {
        'username': user.username,
        'message': message,
        'url': url,
        'uuid': user.profile.uuid,
    })


def get_index_items(request, model, **kwargs):
    """
    """
    context = {}
    model_name = model._meta.verbose_name
    app_settings_model = kwargs.get('app_settings_model')
    active_nav = kwargs.get('active_nav')
    columns_visible = kwargs.get('columns_visible')
    company_model = kwargs.get('company_model')
    edit_url = kwargs.get('edit_url')
    order_by = kwargs.get('order_by')
    page_size = kwargs.get('page_size')
    search_fields = kwargs.get('search_fields')
    show_search = kwargs.get('show_search')
    if columns_visible:
        context['columns_visible'] = columns_visible
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
    if model_name == 'note' and get_setting(request, app_settings_model,
                                            'exclude_hidden_notes'):
        items = model.objects.exclude(hidden=True)
    else:
        items = model.objects.all()
    # Order items (http://stackoverflow.com/a/20257999/185820)
    if order_by is not None:
        items = items.order_by(*order_by)
    # Don't show items to anon
    if not request.user.is_authenticated:
        items = []
    # Per model extras
    if model_name == 'note':
        context['note_stats'] = get_note_stats(model)
    elif model_name == 'time':
        context['total_hours'] = get_total_hours(items)
    # Paginate if paginated
    if paginated:
        page_size = get_setting(
            request, app_settings_model, 'page_size', page_size=page_size)
        items = paginate(items, page, page_size)
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['page'] = page
    context['paginated'] = paginated
    context['show_search'] = show_search
    items = set_items_name(model_name, items=items)
    context['items'] = items
    return context


def get_invoice_totals(model):
    invoices = model.objects.filter(last_payment_date=None)
    invoice_amount = invoice_cog = 0
    for invoice in invoices:
        if invoice.amount:
            invoice_amount += invoice.amount
        if invoice.cog:
            invoice_cog += invoice.cog
    return invoice_amount, invoice_amount - invoice_cog


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
    elif query == 'values':  # plot
        values = request.GET.get('values')
        if values:
            values = values.split(' ')
        else:
            values = []
        values = [i.split(',') for i in values]
        return values
    elif query == 'checkbox':
        cb_query = {}
        cb_active = request.POST.get('checkbox-active')
        cb_subscribe = request.POST.get('checkbox-subscribe')
        cb_condition = (  # if any of these exist
            cb_active == 'on' or cb_active == 'off' or cb_subscribe == 'on' or
            cb_subscribe == 'off')
        cb_query['active'] = cb_active
        cb_query['subscribe'] = cb_subscribe
        cb_query['condition'] = cb_condition
        return cb_query
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
    model_name = model._meta.verbose_name
    for field in search_fields:
        query.append(Q(**{field + '__icontains': search}))
    items = model.objects.filter(reduce(OR, query))
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['show_search'] = True
    items = set_items_name(model_name, items=items)
    context['items'] = items
    return context


def get_setting(request, app_settings_model, setting, page_size=None):
    """
    Allow user to override global setting
    """
    if not request.user.is_authenticated:
        return
    dashboard_override = user_pref = None
    app_settings = app_settings_model.get_solo()
    if setting == 'icon_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.icon_size
        if user_pref:
            return user_pref
        else:
            return app_settings.icon_size
    elif setting == 'page_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.page_size
        if user_pref:
            return user_pref
        elif page_size:  # View's page_size preference
            return page_size
        else:
            return app_settings.page_size
    elif setting == 'dashboard_choices':
        dashboard_choices = app_settings.dashboard_choices
        dashboard_override = has_profile = False
        if hasattr(request.user, 'profile'):
            has_profile = True
        if has_profile:
            dashboard_override = request.user.profile.dashboard_override
        if has_profile and dashboard_override:
            dashboard_choices = request.user.profile.dashboard_choices
        return dashboard_choices
    elif setting == 'exclude_hidden_notes':
        return app_settings.exclude_hidden_notes


def get_template_and_url_names(model_name, page_type=None):
    """
    """
    if page_type == 'view':
        url_name = URL_NAMES[model_name][0]
        template_name = '%s.html' % url_name
        return template_name, url_name
    elif page_type == 'edit':
        template_name = '%s.html' % URL_NAMES[model_name][1]
        return template_name
    elif page_type == 'home':
        url_name = 'home'
        return url_name
    elif page_type == 'index':
        url_name = URL_NAMES[model_name][2]
        return url_name


def get_times_for_obj(obj, time_model):
    model_name = obj._meta.verbose_name
    if model_name == 'invoice':
        times_project = time_model.objects.filter(
            invoiced=False, project=obj.project, estimate=None, invoice=None)
        times_invoice = time_model.objects.filter(invoice=obj)
        times = times_project | times_invoice
    elif model_name == 'project':
        times = time_model.objects.filter(
            invoiced=False, estimate=None, invoice=None, project=obj)
    return times


def get_total_hours(items):
    total_hours = items.aggregate(hours=Sum(F('hours')))
    total_hours = total_hours['hours']
    return total_hours


def gravatar_url(email):
    """
    MD5 hash of email address for use with Gravatar
    """
    return django_settings.GRAVATAR_URL % md5(email.lower()).hexdigest()


def set_items_name(model_name, items=None, _items={}):
    """
    Share templates by returning dictionary of items e.g.
        for item in items.reports
    instead of:
        for item in reports
    """
    _items[ITEMS_NAME[model_name]] = items
    return _items


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


def get_page_items(request, **kwargs):
    app_settings_model = kwargs.get('app_settings_model')
    company_model = kwargs.get('company_model')
    columns_visible = kwargs.get('columns_visible')
    contact_model = kwargs.get('contact_model')
    contract_model = kwargs.get('contract_model')
    estimate_model = kwargs.get('estimate_model')
    invoice_model = kwargs.get('invoice_model')
    model = kwargs.get('model')
    note_model = kwargs.get('note_model')
    profile_model = kwargs.get('profile_model')
    project_model = kwargs.get('project_model')
    report_model = kwargs.get('report_model')
    order_by = kwargs.get('order_by')
    pk = kwargs.get('pk')
    time_model = kwargs.get('time_model')
    user_model = kwargs.get('user_model')
    context = {}
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    items = None
    if company_model:
        company = company_model.get_solo()
        context['company'] = company
    if columns_visible:
        context['columns_visible'] = columns_visible
    if model:
        model_name = model._meta.verbose_name
        context['model_name'] = model_name
        if model_name == 'app settings':
            app_settings = app_settings_model.get_solo()
            context['items'] = get_fields([app_settings, ])  # table_items.html
            context['active_tab'] = 'system'
            context['active_nav'] = 'dropdown'
        elif model_name == 'contract settings':
            contract_settings = model.get_solo()
            context['items'] = get_fields(
                [contract_settings, ])  # table_items.html
            context['active_tab'] = 'contract'
            context['active_nav'] = 'dropdown'
        elif model_name == 'client':
            client = get_object_or_404(model, pk=pk)
            contacts = contact_model.objects.filter(client=client)
            contracts = contract_model.objects.filter(client=client)
            projects = project_model.objects.filter(client=client)
            context['active_nav'] = 'client'
            context['contacts'] = contacts
            context['contracts'] = contracts
            context['edit_url'] = 'client_edit'
            context['item'] = client
            context['notes'] = client.note.all()
            context['projects'] = projects
        elif model_name == 'Company':
            company_settings = model.get_solo()
            context['items'] = get_fields(
                [company_settings, ])  # table_items.html
            context['active_nav'] = 'dropdown'
            context['active_tab'] = 'company'
        elif model_name == 'contact':
            contact = get_object_or_404(model, pk=pk)
            mail = get_query(request, 'mail')
            if mail:
                messages.add_message(request, messages.SUCCESS, 'Mail sent!')
            context['active_nav'] = 'contact'
            context['edit_url'] = 'contact_edit'
            context['items'] = get_fields([contact, ])  # table_items.html
            context['item'] = contact
        elif model_name == 'contract':
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
        elif model_name == 'estimate':
            estimate = get_object_or_404(model, pk=pk)
            if not estimate.is_sow:
                doc_type = model_name
            else:
                doc_type = 'statement of work'
            pdf = get_query(request, 'pdf')
            times_client = time_model.objects.filter(
                client=estimate.client,
                estimate=None,
                project=None,
                invoiced=False,
                invoice=None)
            times_estimate = time_model.objects.filter(estimate=estimate)
            times = times_client | times_estimate
            times = times.order_by(*order_by['time'])
            times = set_invoice_totals(times, estimate=estimate)
            context['active_nav'] = 'estimate'
            context['document_type'] = doc_type
            context['entries'] = times
            context['edit_url'] = 'estimate_edit'
            context['item'] = estimate
            context['pdf'] = pdf
        if model_name == 'file':
            file_obj = get_object_or_404(model, pk=pk)
            context['active_nav'] = 'dropdown'
            context['edit_url'] = 'file_edit'
            context['item'] = file_obj
        elif model_name == 'invoice':
            invoice = get_object_or_404(model, pk=pk)
            times = get_times_for_obj(invoice, time_model)
            times = times.order_by(*order_by['time'])
            times = set_invoice_totals(times, invoice=invoice)
            last_payment_date = invoice.last_payment_date
            pdf = get_query(request, 'pdf')
            context['active_nav'] = 'invoice'
            context['document_type'] = model_name
            context['edit_url'] = 'invoice_edit'  # Delete modal
            context['entries'] = times
            context['item'] = invoice
            context['invoice'] = True
            context['last_payment_date'] = last_payment_date
            context['pdf'] = pdf
        elif model_name == 'project':
            project = get_object_or_404(model, pk=pk)
            contacts = contact_model.objects.all()
            items = set_items_name('contact', items=contacts)
            estimates = estimate_model.objects.filter(
                project=project, accepted_date=None)
            items = set_items_name('estimate', items=estimates, _items=items)
            invoices = invoice_model.objects.filter(
                project=project, last_payment_date=None)
            items = set_items_name('invoice', items=invoices, _items=items)
            times = get_times_for_obj(project, time_model)
            times = times.order_by(*order_by['time'])
            items = set_items_name('time', items=times, _items=items)
            users = user_model.objects.filter(project=project)
            items = set_items_name('user', items=users, _items=items)
            context['active_nav'] = 'project'
            context['edit_url'] = 'project_edit'  # Delete modal
            context['item'] = project
            context['items'] = items
        elif model_name == 'proposal':
            proposal = get_object_or_404(model, pk=pk)
            pdf = get_query(request, 'pdf')
            context['active_nav'] = 'dropdown'
            context['edit_url'] = 'proposal_edit'  # Delete modal
            context['item'] = proposal
            context['pdf'] = pdf
        elif model_name == 'time':
            time_entry = get_object_or_404(model, pk=pk)
            context['active_nav'] = 'time'
            context['edit_url'] = 'time_edit'  # Delete modal
            context['item'] = time_entry
        elif model_name == 'user':
            user = get_object_or_404(model, pk=pk)
            projects = project_model.objects.filter(
                team__in=[user, ], active=True)
            projects = projects.order_by(*order_by['project'])
            times = time_model.objects.filter(
                estimate=None, invoiced=False, user=user)
            times = times.order_by(*order_by['time'])
            contacts = contact_model.objects.all()
            context['active_nav'] = 'dropdown'
            context['item'] = user
            context['items'] = get_fields([user.profile, ])  # table_items.html
            context['profile'] = profile_model.objects.get_or_create(
                user=user)[0]
            context['projects'] = projects
            context['times'] = times
    else:  # home
        if request.user.is_authenticated:
            # Items
            invoices = invoice_model.objects.filter(last_payment_date=None)
            items = set_items_name('invoice', items=invoices)
            notes = note_model.objects.filter(active=True)
            notes = notes.order_by(*order_by['note'])
            items = set_items_name('note', items=notes, _items=items)
            projects = project_model.objects.filter(active=True, hidden=False)
            projects = projects.order_by(*order_by['project'])
            items = set_items_name('project', items=projects, _items=items)
            times = time_model.objects.filter(
                invoiced=False, project__active=True, user=request.user)
            times = times.order_by(*order_by['time'])
            items = set_items_name('time', items=times, _items=items)
            # Plot
            plot_items = report_model.objects.filter(active=True)
            # Totals
            gross, net = get_invoice_totals(invoice_model)
            context['city_data'] = get_client_city(request)
            context['dashboard_choices'] = get_setting(
                request, app_settings_model, 'dashboard_choices')
            context['gross'] = gross
            context['invoices'] = invoices
            context['items'] = items
            context['net'] = net
            context['notes'] = notes
            context['note_stats'] = get_note_stats(note_model)
            context['plot_items'] = plot_items
            context['projects'] = projects
            context['times'] = times
            context['total_hours'] = get_total_hours(times)
    return context


def is_allowed_to_view(model,
                       pk,
                       request,
                       app_settings_model=None,
                       profile_model=None):
    """
    Normal users can only see their own time entries
    """
    msg = 'Sorry, you are not allowed to see that.'
    time_entry = get_object_or_404(model, pk=pk)
    if not time_entry.user and not request.user.is_staff:
        messages.add_message(request, messages.WARNING, msg)
        return HttpResponseRedirect(reverse('home'))
    if (not time_entry.user.username == request.user.username and
            not request.user.is_staff):
        messages.add_message(request, messages.WARNING, msg)
        return HttpResponseRedirect(reverse('home'))
    else:
        context = get_page_items(
            request,
            app_settings_model=app_settings_model,
            model=model,
            profile_model=profile_model,
            pk=pk)
        return render(request, 'time.html', context)


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
    model_name = obj._meta.verbose_name
    template_name, url_name = get_template_and_url_names(
        model_name, page_type='edit')
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def obj_remove(obj):
    model_name = obj._meta.verbose_name
    if model_name == 'time':
        url_name = get_template_and_url_names(
            model_name, page_type='home')  # Redir to home
    else:
        url_name = get_template_and_url_names(
            model_name, page_type='index')  # Redir to index
    obj.delete()
    return HttpResponseRedirect(reverse(url_name))


def obj_edit(obj, pk=None):
    model_name = obj._meta.verbose_name
    template_name, url_name = get_template_and_url_names(
        model_name, page_type='view')  # Redir to view
    # New or existing object
    kwargs = {}
    if pk:  # Special cases for settings
        if model_name == 'Company':
            return HttpResponseRedirect(reverse(url_name))
        elif model_name == 'app settings':
            return HttpResponseRedirect(reverse(url_name))
        elif model_name == 'contract settings':
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


def set_relationship(obj,
                     request,
                     client_model=None,
                     company_model=None,
                     estimate_model=None,
                     invoice_model=None,
                     project_model=None):
    model_name = obj._meta.verbose_name
    if model_name == 'contact':
        query_client = get_query(request, 'client')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            obj.client = client
            obj.save()
            return True
    elif model_name == 'estimate' or model_name == 'invoice':
        query_project = get_query(request, 'project')
        if query_project:
            project = get_object_or_404(project_model, pk=query_project)
            obj.client = project.client
            obj.project = project
            obj.save()
    elif model_name == 'note':
        query_client = get_query(request, 'client')
        query_company = get_query(request, 'company')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            client.note.add(obj)
            client.save()
            return True
        elif query_company:
            company = company_model.get_solo()
            company.note.add(obj)
            company.save()
    elif model_name == 'project':
        query_client = get_query(request, 'client')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            obj.client = client
            obj.save()
    elif model_name == 'time':
        obj.user = request.user
        query_estimate = get_query(request, 'estimate')
        query_invoice = get_query(request, 'invoice')
        query_project = get_query(request, 'project')
        if not request.user.is_staff:  # Staff have more than one project
            user_projects = project_model.objects.filter(team__in=[obj.user, ])
            if len(user_projects) > 0:
                obj.project = user_projects[0]
                obj.task = obj.project.task
        if query_estimate:
            estimate = get_object_or_404(estimate_model, pk=query_estimate)
            obj.estimate = estimate
        if query_invoice:
            invoice = get_object_or_404(invoice_model, pk=query_invoice)
            obj.invoice = invoice
        if query_project:
            project = get_object_or_404(project_model, pk=query_project)
            obj.project = project
            obj.task = project.task
        obj.save()
        return True


def set_invoice_totals(times, estimate=None, invoice=None):
    """
    Set invoice, estimate and time totals
    """
    invoice_amount = invoice_cog = 0
    time_entry_amount = time_entry_cog = 0
    for time_entry in times:
        hours = time_entry.hours
        if time_entry.task:
            rate = time_entry.task.rate
            time_entry_amount = rate * hours
        if time_entry.user:
            rate = time_entry.user.profile.rate
            if rate:
                time_entry_cog = rate * hours
        time_entry.amount = '%.2f' % time_entry_amount
        time_entry.cog = '%.2f' % time_entry_cog
        invoice_amount += time_entry_amount
        invoice_cog += time_entry_cog
    if invoice:
        invoice.amount = '%.2f' % invoice_amount
        invoice.cog = '%.2f' % invoice_cog
        invoice.save()
    elif estimate:
        estimate.amount = '%.2f' % invoice_amount
        estimate.save()
    return times
