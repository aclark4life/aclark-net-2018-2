from collections import OrderedDict
from boto.exception import BotoServerError
from decimal import Decimal
from django.conf import settings
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
# from django.utils.html import strip_tags
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
    'estimate': ('estimate', 'estimate_edit', 'estimate_index'),
    'invoice': ('invoice', 'invoice_edit', 'invoice_index'),
    'newsletter': ('newsletter', 'newsletter_edit', 'newsletter_index'),
    'note': ('note', 'note_edit', 'note_index'),
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
            messages.add_message(request, messages.INFO,
                                 'User added to contacts!')
            return HttpResponseRedirect(reverse('contact_index'))


def check_boxes(obj, checkbox, checkbox_subscribed, refer):
    if checkbox == 'on' or checkbox == 'off':
        if checkbox == 'on':
            obj.active = True
        else:
            obj.active = False
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
                    entry.notes, entry.hours)
            else:
                notes += '%s <strong>%s hours</strong>.' % (entry.notes,
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


def create_form(model,
                form_model,
                projects=[],
                project=None,
                clients=[],
                client=None,
                gross=None,
                net=None,
                tasks=[],
                task=None):
    form = form_model()
    # Populate new report with gross and net calculated
    # from active invoices
    if form._meta.model._meta.verbose_name == 'report':
        obj = model(gross=gross, net=net)
        form = form_model(instance=obj)
    # Limit time entry project, client
    # and task choices
    if form._meta.model._meta.verbose_name == 'time':
        form.fields['project'].queryset = projects
        form.fields['client'].queryset = clients
        form.fields['task'].queryset = tasks
    # Limit project client choices
    # if form._meta.model._meta.verbose_name == 'project':
    #     form.fields['client'].queryset = clients
    # Populate time entry form fields with project, client
    # and task values
    if project and model._meta.verbose_name == 'time':
        entry = model(
            project=project, client=project.client, task=project.task)
        form = form_model(instance=entry)
    # Populate invoice with project
    elif project and model._meta.verbose_name == 'invoice':
        entry = model(project=project, client=project.client)
        form = form_model(instance=entry)
    # Populate time entry form fields with client and
    # task values
    elif client and task:
        entry = model(client=client, task=task)
        form = form_model(instance=entry)
    # Populate project entry form fields with client value
    elif client:
        entry = model(client=client)
        form = form_model(instance=entry)
    # Populate time entry form fields with task value
    elif task:
        entry = model(task=task)
        form = form_model(instance=entry)
    return form


def daily_burn(project):
    try:
        days = (project.end_date - project.start_date).days
        hours = project.budget
        burn = hours / days
        return '%.2f' % burn
    except (TypeError, ZeroDivisionError):
        return ''


def dashboard_totals(model):
    results = OrderedDict()
    invoices_active = model.objects.filter(last_payment_date=None)
    invoices_active = invoices_active.order_by('-pk')
    gross = 0
    net = 0
    for invoice in invoices_active:
        results[invoice] = {}
        results[invoice]['subtotal'] = invoice.subtotal
        results[invoice]['amount'] = invoice.amount
        if invoice.subtotal:
            gross += invoice.subtotal
        if invoice.amount:
            net += invoice.amount
    return gross, net, invoices_active


def edit_amounts(obj, amount, subtotal, paid_amount, paid, url_name=''):
    kwargs = {}
    if amount and subtotal and paid_amount and paid:
        obj.amount = amount
        obj.last_payment_date = timezone.now()
        obj.subtotal = subtotal
        obj.paid_amount = paid_amount
        obj.save()
        return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))
    elif amount and subtotal and paid_amount:
        obj.amount = amount
        obj.subtotal = subtotal
        obj.paid_amount = paid_amount
        obj.save()
        return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))
    elif amount and subtotal:
        obj.amount = amount
        obj.subtotal = subtotal
        obj.save()
        return HttpResponseRedirect(reverse(url_name))
    elif amount:
        obj.amount = amount
        obj.save()
        return HttpResponseRedirect(reverse(url_name))


def edit(
        request,
        form_model,
        model,
        url_name,
        template_name,
        active_nav=None,
        amount=None,
        client=None,
        clients=[],
        company=None,
        company_note=None,
        contract_settings=None,
        context={},
        gross=None,
        invoices_active=None,  # for reporting
        log_model=None,
        net=None,
        pk=None,
        paid_amount=None,
        paid=None,
        project=None,
        projects=[],
        subtotal=None,
        task=None,
        tasks=[]):
    obj = None
    refer = request.META['HTTP_REFERER']
    if pk is None:
        form = create_form(
            model,
            form_model,
            projects=projects,
            project=project,
            clients=clients,
            client=client,
            gross=gross,
            net=net,
            tasks=tasks,
            task=task)
    else:
        obj = get_object_or_404(model, pk=pk)
        form = form_model(instance=obj)
    if request.method == 'POST':
        if pk is None:
            form = form_model(request.POST)
        else:
            checkbox = request.POST.get('checkbox')
            checkbox_subscribed = request.POST.get('checkbox-subscribed')
            copy = request.POST.get('copy')
            delete = request.POST.get('delete')
            # Copy or delete
            if copy:
                return obj_copy(obj, url_name)
            if delete:
                return obj_delete(obj, company, request=request)
            # Check boxes
            if (checkbox == 'on' or checkbox == 'off' or
                    checkbox_subscribed == 'on' or
                    checkbox_subscribed == 'off'):
                return check_boxes(obj, checkbox, checkbox_subscribed, refer)
            # Edit amounts
            if amount or subtotal or paid_amount or paid:
                return edit_amounts(
                    obj,
                    amount,
                    subtotal,
                    paid_amount,
                    paid,
                    url_name=url_name)
            form = form_model(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return obj_edit(
                obj,
                company=company,
                contract_settings=contract_settings,
                company_note=company_note,
                log_model=log_model,
                pk=pk,
                request=request)
    context['active_nav'] = active_nav
    context['form'] = form
    context['item'] = obj
    context['pk'] = pk
    return render(request, template_name, context)


def entries_total(queryset):
    """
    Add estimate and invoice time entries, could be an aggregate
    (https://docs.djangoproject.com/en/1.9/topics/db/aggregation/)
    """
    entries = OrderedDict()
    total = 0
    running_total_co = 0
    running_total_dev = 0
    running_total_hours = 0
    for entry in queryset:
        entries[entry] = {}
        hours = entry.hours
        if hours:
            running_total_hours += hours
        entries[entry]['date'] = entry.date
        entries[entry]['hours'] = hours
        entries[entry]['notes'] = entry.notes
        entries[entry]['pk'] = entry.pk
        entries[entry]['user'] = entry.user
        entries[entry]['task'] = entry.task
        line_total = 0
        line_total_co = 0
        line_total_dev = 0
        line_total_client = 0
        if entry.task:
            rate = entry.task.rate
            entries[entry]['rate'] = rate
            if rate:
                line_total_co = rate * hours
            entries[entry]['line_total_co'] = line_total_co
            running_total_co += line_total_co
        if entry.user and entry.project:
            if hasattr(entry.user, 'profile'):
                if entry.user.profile.rate:
                    line_total_dev = entry.user.profile.rate * hours
                entries[entry]['line_total_dev'] = line_total_dev
                running_total_dev += line_total_dev
        if entry.project:
            line_total = line_total_co - line_total_dev
            line_total_client = line_total_co
            entries[entry]['line_total_client'] = '%.2f' % line_total_client
        else:
            line_total = line_total_co
        entries[entry]['line_total'] = '%.2f' % line_total
    total = running_total_co - running_total_dev
    return (entries, running_total_co, running_total_dev, running_total_hours,
            total)


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


def get_setting(request, settings_model, setting, page_size=None):
    """
    Allow user to override global setting
    """
    if not request.user.is_authenticated:
        return
    override = user_pref = None
    settings = settings_model.get_solo()
    if setting == 'icon_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.icon_size
        if user_pref:
            return user_pref
        else:
            return settings.icon_size
    if setting == 'page_size':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.page_size
        if user_pref:
            return user_pref
        elif page_size:  # View's page_size preference
            return page_size
        else:
            return settings.page_size
    if setting == 'dashboard_choices':
        if hasattr(request.user, 'profile'):
            user_pref = request.user.profile.dashboard_choices
            override = request.user.profile.override_dashboard
        if override:
            return user_pref
        else:
            return settings.dashboard_choices
    if setting == 'dashboard_order':
        if settings.dashboard_order:
            return settings.dashboard_order
        else:
            # XXX How to get default field value with knowing index?
            # Also don't like splitting on ', '.
            return settings._meta.fields[6].get_default().split(', ')


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
                       app_settings=None,
                       edit_url='',
                       order_by='-updated',
                       request=None):
    context = {}
    query = []
    for field in search_fields:
        query.append(Q(**{field + '__icontains': search}))
    items = model.objects.filter(reduce(OR, query)).order_by(order_by)
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings, 'icon_size')
    context['items'] = items
    context['show_search'] = True
    return context


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


def gravatar_url(email):
    """
    MD5 hash of email address for use with Gravatar
    """
    return settings.GRAVATAR_URL % md5(email.lower()).hexdigest()


def index_items(request,
                model,
                search_fields,
                filters={},
                order_by=(),
                app_settings=None,
                active_nav='',
                edit_url='',
                page_size=None,
                show_search=False):
    """
    """
    context = {}
    page = get_query(request, 'page')
    paginated = get_query(request, 'paginated')
    search = get_query(request, 'search')
    # Search is easy
    if request.method == 'POST':
        if search == u'':  # Empty search returns none
            context['show_search'] = True
            return context
        else:
            return get_search_results(
                model,
                search_fields,
                search,
                active_nav=active_nav,
                app_settings=app_settings,
                edit_url=edit_url,
                request=request)
    # Not a search
    if filters:
        items = model.objects.filter(**filters)
    else:
        items = model.objects.all()
    # Reorder items
    if order_by:
        # http://stackoverflow.com/a/20257999/185820
        if len(order_by) > 1:
            items = items.order_by(order_by[0], order_by[1])
        else:
            items = items.order_by(order_by[0])
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
    # Don't show items to anon
    if not request.user.is_authenticated:
        items = []
    # Paginate if paginated
    if paginated:
        page_size = get_setting(
            request, app_settings, 'page_size', page_size=page_size)
        items = paginate(items, page, page_size)
    context['active_nav'] = active_nav
    context['edit_url'] = edit_url
    context['icon_size'] = get_setting(request, app_settings, 'icon_size')
    context['items'] = items
    context['page'] = page
    context['paginated'] = paginated
    context['show_search'] = show_search
    return context


def last_month():
    """
    Returns last day of last month
    """
    first = timezone.now().replace(day=1)
    return first - timezone.timedelta(days=1)


def obj_copy(obj, url_name):
    dup = obj
    dup.pk = None
    dup.save()
    kwargs = {}
    kwargs['pk'] = dup.pk
    template_name, url_name = get_template_and_url_names(
        obj._meta.verbose_name, page_type='edit')
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def obj_delete(obj, company, request=None):
    url_name = get_template_and_url_names(
        obj._meta.verbose_name, page_type='index')  # Redir to index
    # Decrement invoice counter
    if (obj._meta.verbose_name == 'invoice' and company.invoice_counter):
        company.invoice_counter -= 1
        company.save()
    # Decrement estimate counter
    if (obj._meta.verbose_name == 'estimate' and company.estimate_counter):
        company.estimate_counter -= 1
        company.save()
    if (obj._meta.verbose_name == 'time' and not request.user.is_staff):
        url_name = 'home'  # Redir to home
    obj.delete()
    return HttpResponseRedirect(reverse(url_name))


def obj_edit(obj,
             company=None,
             contract_settings=None,
             company_note=None,
             log_model=None,
             request=None,
             pk=None):
    template_name, url_name = get_template_and_url_names(
        obj._meta.verbose_name, page_type='view')  # Redir to view
    # Time entry
    if obj._meta.verbose_name == 'time' and pk is None:
        # Assign user to time entry on creation
        obj.user = User.objects.get(username=request.user)
        obj.save()
        # Send mail when time entry created
        if hasattr(obj.user, 'profile'):
            if obj.user.profile.notify:
                subject = 'Time entry'
                message = '%s entered time! %s' % (
                    obj.user.username,
                    obj.get_absolute_url(request.get_host()))
                try:
                    send_mail(request, subject, message, settings.EMAIL_FROM)
                except BotoServerError:
                    log = log_model(entry='Could not send mail.')
                    log.save()
    # Assign and increment invoice counter
    if (obj._meta.verbose_name == 'invoice' and company.invoice_counter and
            pk is None):
        company.invoice_counter += 1
        company.save()
        obj.document_id = company.invoice_counter
        obj.save()
    # Assign and increment estimate counter
    if (obj._meta.verbose_name == 'estimate' and company.estimate_counter and
            pk is None):
        company.estimate_counter += 1
        company.save()
        obj.document_id = company.estimate_counter
        obj.save()
    # Assign client to invoice
    if obj._meta.verbose_name == 'invoice' and obj.project:
        if obj.project.client and not obj.client:
            obj.client = obj.project.client
            obj.save()
    # Assign default contract fields
    if obj._meta.verbose_name == 'contract' and pk is None:
        text = ''
        for field in contract_settings._meta.fields:
            if field.description == 'Text' and field.name != 'body':
                text = ''.join([text, '<h2>', field.verbose_name, '</h2>'])
                text = ''.join([
                    text, '<p>', getattr(contract_settings, field.name), '</p>'
                ])
        setattr(obj, 'body', text)
        obj.save()
    if obj._meta.verbose_name == 'note' and company_note:
        company.note.add(obj)
        company.save()
    kwargs = {}
    if pk:
        kwargs['pk'] = pk
    else:
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
    sender = settings.EMAIL_FROM
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
