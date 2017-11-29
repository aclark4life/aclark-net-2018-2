from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from faker import Faker
from functools import reduce
from operator import or_ as OR
from .fields import get_fields
from .geo import get_geo_ip_data
from .info import get_note_info
from .info import get_recipients
from .info import get_setting
from .obj import get_template_and_url
from .obj import get_times_for_obj
from .obj import obj_copy
from .obj import obj_redir
from .obj import obj_remove
from .obj import obj_sent
from .page import paginate
from .query import get_query_string
from .query import set_check_boxes
from .total import get_total_amount
from .total import get_total_cost
from .total import get_total_hours
from .total import set_total_amount

fake = Faker()
gravatar_url = 'https://www.gravatar.com/avatar/%s'


def edit(request, **kwargs):
    context = {}
    obj = None
    app_settings_model = kwargs.get('app_settings_model')
    client_model = kwargs.get('client_model')
    company_model = kwargs.get('company_model')
    contact_model = kwargs.get('contact_model')
    estimate_model = kwargs.get('estimate_model')
    form_model = kwargs.get('form_model')
    invoice_model = kwargs.get('invoice_model')
    model = kwargs.get('model')
    note_model = kwargs.get('note_model')
    pk = kwargs.get('pk')
    project_model = kwargs.get('project_model')
    user_model = kwargs.get('user_model')
    model_name = None
    if model:
        model_name = model._meta.verbose_name
        context['active_nav'] = model_name
    if pk is None:  # New
        form = get_form(
            client_model=client_model,
            form_model=form_model,
            invoice_model=invoice_model,
            model=model,
            project_model=project_model,
            user_model=user_model,
            request=request)
    else:  # Existing
        obj = get_object_or_404(model, pk=pk)
        if model_name == 'user':  # One-off to edit user profile
            obj = obj.profile
        form = get_form(form_model=form_model, obj=obj)
    if request.method == 'POST':
        ref = request.META.get('HTTP_REFERER')
        if pk is None:
            if model_name == 'user':  # One-off to create user
                username = fake.text()[:150]
                new_user = model.objects.create_user(username=username)
            form = form_model(request.POST)
        else:
            copy = get_query_string(request, 'copy')  # Copy or delete
            delete = get_query_string(request, 'delete')
            if copy:
                return obj_copy(obj)
            if delete:
                return obj_remove(obj)
            query_checkbox = get_query_string(request,
                                              'checkbox')  # Check boxes
            if query_checkbox['condition']:
                return set_check_boxes(obj, query_checkbox, ref,
                                       app_settings_model)
            sent = get_query_string(request, 'sent')
            if sent:
                return obj_sent(obj, ref)
            not_sent = get_query_string(request, 'not_sent')
            if not_sent:
                return obj_sent(obj, ref, invoiced=False)
            form = form_model(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            if model_name == 'user':  # One-off to create profile
                if not obj.user:  # for new user
                    obj.user = new_user
                    obj.save()
            set_relationship(
                obj,
                request,
                client_model=client_model,
                company_model=company_model,
                estimate_model=estimate_model,
                invoice_model=invoice_model,
                model=model,
                project_model=project_model)
            # if model_name == 'time':
            #     mail_proc(obj, request=request)  # XXX Use signal?
            return obj_redir(obj, pk=pk)
    context['form'] = form
    context['is_staff'] = request.user.is_staff
    context['item'] = obj
    context['pk'] = pk
    if company_model:
        company = company_model.get_solo()
        company_name = company.name
        company_address = company.address
        company_currency_symbol = company.currency_symbol
        context['company_name'] = company_name
        context['company_address'] = company_address
        context['company_currency_symbol'] = company_currency_symbol
    elif contact_model:
        model_name = contact_model._meta.verbose_name
    elif note_model:
        model_name = note_model._meta.verbose_name
    template_name = get_template_and_url(
        model_name=model_name, page_type='edit')
    return render(request, template_name, context)


def get_form(**kwargs):
    """
    Return appropriate form based on new or edit
    """
    client_model = kwargs.get('client_model')
    form_model = kwargs.get('form_model')
    invoice_model = kwargs.get('invoice_model')
    model = kwargs.get('model')
    obj = kwargs.get('obj')
    request = kwargs.get('request')
    project_model = kwargs.get('project_model')
    user_model = kwargs.get('user_model')
    query_client = None
    query_project = None
    query_user = None
    if request:
        query_user = get_query_string(request, 'user')
        query_client = get_query_string(request, 'client')
    if obj:  # Existing object
        model_name = obj._meta.verbose_name
        if model_name == 'note':  # Populate form with tags already set
            form = form_model(initial={'tags': obj.tags.all()}, instance=obj)
        else:
            form = form_model(instance=obj)
    else:  # New object
        initial = {'send_html': True}
        if model:
            model_name = model._meta.verbose_name
            if model_name == 'report' and invoice_model:  # Populate new report
                # with gross
                invoices = invoice_model.objects.filter(last_payment_date=None)
                projects = project_model.objects.filter(invoice__in=invoices)
                gross = get_total_amount(invoices)
                cost = get_total_cost(projects)
                net = gross - cost
                obj = model(cost=cost, gross=gross, net=net)
                form = form_model(instance=obj, initial={'invoices': invoices})
            elif model_name == 'contact':  # Populate new contact
                # with appropriate fields
                # if query_user:
                #     user = get_object_or_404(user_model, pk=query_user)
                #     obj = model(email=user.email)
                if query_client:
                    client = get_object_or_404(client_model, pk=query_client)
                    obj = model(client=client)
                form = form_model(instance=obj)
            elif model_name == 'estimate':
                if query_user:
                    user = get_object_or_404(user_model, pk=query_user)
                    obj = model(user=user)
                elif query_project:
                    project = get_object_or_404(
                        project_model, pk=query_project)
                    obj = model(project=project)
                form = form_model(instance=obj)
            elif model_name == 'invoice':
                now = timezone.now()
                obj = model(subject="%s" % now.strftime('%B %Y'))
                form = form_model(instance=obj)
            else:
                form = form_model(initial=initial)
        else:
            form = form_model(initial=initial)
    return form


def get_index_items(**kwargs):
    """
    """
    context = {}
    app_settings_model = kwargs.get('app_settings_model')
    columns_visible = kwargs.get('columns_visible')
    company_model = kwargs.get('company_model')
    model = kwargs.get('model')
    order_by = kwargs.get('order_by')
    page_size = kwargs.get('page_size')
    request = kwargs.get('request')
    search_fields = kwargs.get('search_fields')
    model_name = model._meta.verbose_name
    edit_url = '%s_edit' % model_name
    view_url = '%s_view' % model_name
    if columns_visible:
        context['columns_visible'] = columns_visible
    if company_model:
        company = company_model.get_solo()
        company_name = company.name
        company_address = company.address
        company_currency_symbol = company.currency_symbol
        context['company_name'] = company_name
        context['company_address'] = company_address
        context['company_currency_symbol'] = company_currency_symbol
    page = get_query_string(request, 'page')
    paginated = get_query_string(request, 'paginated')
    search = get_query_string(request, 'search')
    if request:
        context['is_staff'] = request.user.is_staff
    # Search is easy
    if request.method == 'POST':
        if search == u'':  # Empty search returns none
            return context
        else:
            return get_search_results(
                context,
                model,
                search_fields,
                search,
                app_settings_model=app_settings_model,
                edit_url=edit_url,
                view_url=view_url,
                order_by=order_by,
                request=request)
    # Not a search
    items = model.objects.all()
    if order_by is not None:  # Order items
        # http://stackoverflow.com/a/20257999/185820
        items = items.order_by(*order_by)
    if not request.user.is_authenticated:  # Don't show items to anon
        items = []
    if model_name == 'note':  # Per model extras
        context['note_info'] = get_note_info(model)
    elif model_name == 'invoice':
        context['show_invoice_sent'] = 'true'
        context['show_invoice_subject'] = 'true'
        context['show_invoice_user'] = 'false'
    elif model_name == 'time':
        context['total_hours'] = get_total_hours(items)['total']
    if paginated:  # Paginate if paginated
        page_size = get_setting(
            request, app_settings_model, 'page_size', page_size=page_size)
        items = paginate(items, page, page_size)
    context['edit_url'] = edit_url
    context['view_url'] = view_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['icon_color'] = get_setting(request, app_settings_model,
                                        'icon_color')
    context['page'] = page
    context['paginated'] = paginated
    items = set_items(model_name, items=items)
    context['items'] = items
    context['active_nav'] = model_name
    return context


def get_page_items(**kwargs):
    app_settings_model = kwargs.get('app_settings_model')
    company_model = kwargs.get('company_model')
    columns_visible = kwargs.get('columns_visible')
    contact_model = kwargs.get('contact_model')
    contract_model = kwargs.get('contract_model')
    dashboard_item_model = kwargs.get('dashboard_item_model')
    estimate_model = kwargs.get('estimate_model')
    invoice_model = kwargs.get('invoice_model')
    model = kwargs.get('model')
    note_model = kwargs.get('note_model')
    obj = kwargs.get('obj')
    project_model = kwargs.get('project_model')
    report_model = kwargs.get('report_model')
    request = kwargs.get('request')
    order_by = kwargs.get('order_by')
    pk = kwargs.get('pk')
    time_model = kwargs.get('time_model')
    user_model = kwargs.get('user_model')
    context = {}
    items = None
    if company_model:
        company = company_model.get_solo()
        company_name = company.name
        company_address = company.address
        company_currency_symbol = company.currency_symbol
        context['company_name'] = company_name
        context['company_address'] = company_address
        context['company_currency_symbol'] = company_currency_symbol
    if columns_visible:
        context['columns_visible'] = columns_visible
    if model or obj:
        if model:
            model_name = model._meta.verbose_name
        elif obj:
            model_name = obj._meta.verbose_name
        context['model_name'] = model_name
        context['active_nav'] = model_name
        context['edit_url'] = '%s_edit' % model_name
        context['view_url'] = '%s_view' % model_name
        if model_name == 'Settings App':
            app_settings = app_settings_model.get_solo()
            context['items'] = get_fields([
                app_settings,
            ])  # table_items.html
        elif model_name == 'Settings Company':
            company_settings = model.get_solo()
            context['items'] = get_fields([
                company_settings,
            ])  # table_items.html
        elif model_name == 'Settings Contract':
            contract_settings = model.get_solo()
            context['items'] = get_fields([
                contract_settings,
            ])  # table_items.html
        elif model_name == 'client':
            client = get_object_or_404(model, pk=pk)
            contacts = contact_model.objects.filter(client=client)
            contracts = contract_model.objects.filter(client=client)
            projects = project_model.objects.filter(active=True, client=client)
            if order_by:
                projects = projects.order_by(*order_by['project'])
            context['contacts'] = contacts
            context['contracts'] = contracts
            context['item'] = client
            context['notes'] = client.note.all()
            context['projects'] = projects
        elif model_name == 'contact':
            contact = get_object_or_404(model, pk=pk)
            context['items'] = get_fields([
                contact,
            ])  # table_items.html
            context['item'] = contact
        elif model_name == 'contract':
            contract = get_object_or_404(model, pk=pk)
            estimate = contract.statement_of_work
            times = None
            if estimate:
                times = time_model.objects.filter(
                    client=estimate.client,
                    estimate=None,
                    project=None,
                    invoiced=False,
                    invoice=None)
            context['doc_type'] = model_name
            context['item'] = contract
            context['times'] = times
        elif model_name == 'estimate':  # handle obj or model
            if not obj:
                estimate = get_object_or_404(model, pk=pk)
            else:
                estimate = obj
            if estimate.is_sow:
                doc_type = 'statement of work'
            elif estimate.is_to:
                doc_type = 'task order'
            else:
                doc_type = model_name
            times = time_model.objects.filter(estimate=estimate)
            if order_by:
                times = times.order_by(*order_by['time'])
            times = set_total_amount(times, estimate=estimate)
            total_hours = get_total_hours(times)['total']
            context['doc_type'] = doc_type
            context['entries'] = times
            context['item'] = estimate
            context['total_hours'] = total_hours
            context['show_export'] = True
        if model_name == 'file':
            file_obj = get_object_or_404(model, pk=pk)
            context['doc_type'] = model_name
            context['item'] = file_obj
        elif model_name == 'invoice':
            invoice = get_object_or_404(model, pk=pk)
            times = get_times_for_obj(invoice, time_model)
            times = times.order_by(*order_by['time'])
            times = set_total_amount(times, invoice=invoice)
            last_payment_date = invoice.last_payment_date
            total_hours = get_total_hours(times)['total']
            context['doc_type'] = model_name
            context['entries'] = times
            context['item'] = invoice
            context['invoice'] = True
            context['last_payment_date'] = last_payment_date
            context['total_hours'] = total_hours
            context['show_export'] = True
        elif model_name == 'newsletter':
            newsletter = get_object_or_404(model, pk=pk)
            context['doc_type'] = model_name
            context['item'] = newsletter
            mail = get_query_string(request, 'mail')  # Send mail
            if mail:
                mail_proc(newsletter, request=request)  # XXX Use signal?
        elif model_name == 'note':
            note = get_object_or_404(model, pk=pk)
            context['item'] = note
        elif model_name == 'project':
            project = get_object_or_404(model, pk=pk)
            contacts = contact_model.objects.all()
            estimates = estimate_model.objects.filter(
                project=project, is_to=False, is_sow=False)
            invoices = invoice_model.objects.filter(
                project=project, last_payment_date=None)
            times = get_times_for_obj(project, time_model)
            times = times.order_by(*order_by['time'])
            times = set_total_amount(times, project=project)
            users = user_model.objects.filter(project=project)
            items = set_items('contact', items=contacts)
            items = set_items('estimate', items=estimates, _items=items)
            items = set_items('invoice', items=invoices, _items=items)
            items = set_items('time', items=times, _items=items)
            items = set_items('user', items=users, _items=items)
            total_hours = get_total_hours(times, team=users)
            context['cost'] = float(project.cost)
            context['gross'] = float(project.amount)
            context['item'] = project
            context['items'] = items
            context['net'] = float(project.amount) - float(project.cost)
            context['total_hours'] = total_hours
        elif model_name == 'proposal':
            proposal = get_object_or_404(model, pk=pk)
            context['doc_type'] = model_name
            context['item'] = proposal
        elif model_name == 'report':
            report = get_object_or_404(model, pk=pk)
            reports = model.objects.filter(active=True)
            reports.aggregate(cost=Sum(F('cost')))
            reports.aggregate(gross=Sum(F('gross')))
            reports.aggregate(net=Sum(F('net')))
            invoices = report.invoices.all()
            items = set_items('invoice', items=invoices)
            context['item'] = report
            context['items'] = items
            context['reports'] = reports
        elif model_name == 'task':
            task = get_object_or_404(model, pk=pk)
            context['item'] = task
        elif model_name == 'time':
            time_entry = get_object_or_404(model, pk=pk)
            context['item'] = time_entry
        elif model_name == 'user':
            exclude_fields = ('id', 'created', 'updated', 'hidden', 'active',
                              'app_admin', 'is_contact', 'notify', 'published',
                              'dashboard_override', 'dashboard_choices',
                              'editor', 'icon_size', 'icon_color', 'page_size',
                              'preferred_username', 'unit', 'avatar_url')
            user = get_object_or_404(model, pk=pk)
            projects = project_model.objects.filter(
                team__in=[
                    user,
                ], active=True)
            projects = projects.order_by(*order_by['project'])
            times = time_model.objects.filter(
                estimate=None, invoiced=False, user=user)
            times = times.order_by(*order_by['time'])
            contacts = contact_model.objects.all()
            context['item'] = user
            context['items'] = get_fields(
                [
                    user.profile,
                ], exclude_fields=exclude_fields)  # table_items.html
            context['projects'] = projects
            context['times'] = times
    else:  # home
        if request:
            if request.user.is_authenticated:
                # Dashboard
                if request.user.is_staff:  # Staff get a choice of dashboards
                    dashboard_choices = get_setting(
                        request, app_settings_model, 'dashboard_choices')
                else:  # Users get times dashboard only
                    dashboard_choices = 'times'
                dashboard_items = [
                    i.title.lower()
                    for i in dashboard_item_model.objects.all()
                ]
                context['dashboard_choices'] = dashboard_choices
                context['dashboard_items'] = dashboard_items
                # Items
                estimates = estimate_model.objects.filter(
                    accepted_date=None,
                    hidden=False,
                    is_to=False,
                    is_sow=False)
                estimates = estimates.order_by(*order_by['estimate'])
                invoices = invoice_model.objects.filter(last_payment_date=None)
                invoices = invoices.order_by(*order_by['invoice'])
                notes = note_model.objects.filter(active=True, hidden=False)
                notes = notes.order_by(*order_by['note'])
                projects = project_model.objects.filter(
                    active=True, hidden=False)
                projects = projects.order_by(*order_by['project'])
                times = time_model.objects.filter(
                    invoiced=False, user=request.user)
                times = times.order_by(*order_by['time'])
                times = set_total_amount(times)
                items = set_items('estimate', items=estimates)
                items = set_items('invoice', items=invoices)
                items = set_items('note', items=notes, _items=items)
                items = set_items('project', items=projects, _items=items)
                items = set_items('time', items=times, _items=items)
                # Plot
                reports = report_model.objects.filter(active=True)
                reports = reports.order_by(*order_by['report'])
                # Totals
                gross = get_total_amount(invoices)
                ip_address = request.META.get('HTTP_X_REAL_IP')
                context['gross'] = gross
                context['invoices'] = invoices
                context['geo_ip_data'] = get_geo_ip_data(request)
                context['ip_address'] = ip_address
                context['items'] = items
                context['notes'] = notes
                context['note_info'] = get_note_info(note_model)
                context['reports'] = reports
                context['projects'] = projects
                context['show_invoice_sent'] = 'false'
                context['show_invoice_subject'] = 'false'
                context['show_invoice_user'] = 'false'
                context['times'] = times
                total_hours = get_total_hours(times)['total']
                total_cost = get_total_cost(projects)
                context['cost'] = total_cost
                if gross and total_cost:
                    context['net'] = gross - total_cost
                context['total_hours'] = total_hours
    if request:
        context['is_staff'] = request.user.is_staff  # Perms
        context['icon_color'] = get_setting(request, app_settings_model,
                                            'icon_color')  # Prefs
        context['icon_size'] = get_setting(request, app_settings_model,
                                           'icon_size')
        pdf = get_query_string(request, 'pdf')  # Export pdf
        context['pdf'] = pdf
        context['request'] = request  # Include request
    return context


def get_search_results(context,
                       model,
                       search_fields,
                       search,
                       app_settings_model=None,
                       edit_url=None,
                       view_url=None,
                       order_by=None,
                       request=None):
    query = []
    model_name = model._meta.verbose_name
    for field in search_fields:
        query.append(Q(**{field + '__icontains': search}))
    items = model.objects.filter(reduce(OR, query))
    context['active_nav'] = model_name
    context['edit_url'] = edit_url
    context['view_url'] = view_url
    context['icon_size'] = get_setting(request, app_settings_model,
                                       'icon_size')
    context['icon_color'] = get_setting(request, app_settings_model,
                                        'icon_color')
    if order_by is not None:
        items = items.order_by(*order_by)
    items = set_items(model_name, items=items)
    context['items'] = items
    return context


def mail_compose(obj, **kwargs):
    """
    Compose message based on type
    """
    hostname = kwargs.get('hostname')
    mail_from = kwargs.get('mail_from')
    mail_to = kwargs.get('mail_to')
    # Conditionally create message
    model_name = obj._meta.verbose_name
    if model_name == 'newsletter':
        message = obj.text
        subject = obj.subject
    elif model_name == 'time':
        message = '%s' % obj.get_absolute_url(hostname)
        subject = 'Time entry'
    context = {}
    context['mail_from'] = mail_from
    context['mail_to'] = mail_to
    context['message'] = message
    context['subject'] = subject
    return context


def mail_proc(obj, **kwargs):
    """
    """
    # Iterate over recipients, compose and send mail to
    # each.
    request = kwargs.get('request')
    hostname = request.META.get('HTTP_HOST')
    mail_from = django_settings.EMAIL_FROM
    recipients = get_recipients(obj)
    for first_name, email_address in recipients:
        mail_send(**mail_compose(
            obj,
            first_name=first_name,
            hostname=hostname,
            mail_from=mail_from,
            mail_to=email_address,
            request=request))


def mail_send(**kwargs):
    mail_from = kwargs.get('mail_from')
    mail_to = kwargs.get('mail_to')
    message = kwargs.get('message')
    subject = kwargs.get('subject')
    send_mail(subject, message, mail_from, (mail_to, ), fail_silently=False)


def set_items(model_name, items=None, _items={}):
    """
    Share templates by returning dictionary of items e.g.
        for item in items.reports
    instead of:
        for item in reports
    """
    _items['%ss' % model_name] = items
    return _items


def set_relationship(obj, request, **kwargs):
    """
    Sets relationships after create or edit
    """
    client_model = kwargs.get('client_model')
    company_model = kwargs.get('company_model')
    estimate_model = kwargs.get('estimate_model')
    invoice_model = kwargs.get('invoice_model')
    project_model = kwargs.get('project_model')
    model_name = obj._meta.verbose_name
    if model_name == 'contact':
        query_client = get_query_string(request, 'client')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            obj.client = client
            obj.save()
    elif model_name == 'estimate' or model_name == 'invoice':
        query_project = get_query_string(request, 'project')
        if query_project:
            project = get_object_or_404(project_model, pk=query_project)
            obj.client = project.client
            obj.project = project
            obj.save()
    elif model_name == 'note':
        query_client = get_query_string(request, 'client')
        query_company = get_query_string(request, 'company')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            client.note.add(obj)
            client.save()
        elif query_company:
            company = company_model.get_solo()
            company.note.add(obj)
            company.save()
    elif model_name == 'project':
        query_client = get_query_string(request, 'client')
        if query_client:
            client = get_object_or_404(client_model, pk=query_client)
            obj.client = client
            obj.save()
    elif model_name == 'time':
        if not obj.user:  # If no user, set user, else do nothing.
            obj.user = request.user
        query_estimate = get_query_string(request, 'estimate')
        query_invoice = get_query_string(request, 'invoice')
        query_project = get_query_string(request, 'project')
        # if not request.user.is_staff:  # Staff have more than one project
        #     user_projects = project_model.objects.filter(
        #         team__in=[
        #             obj.user,
        #         ])
        #     if len(user_projects) > 0:
        #         obj.project = user_projects[0]
        #         obj.task = obj.project.task
        if query_estimate:
            estimate = get_object_or_404(estimate_model, pk=query_estimate)
            obj.estimate = estimate
        if query_invoice:
            invoice = get_object_or_404(invoice_model, pk=query_invoice)
            obj.invoice = invoice
            obj.save()  # Need save here to set more attrs
            obj.project = invoice.project
            obj.save()  # Need save here to set more attrs
            obj.task = invoice.project.task
        if query_project:
            project = get_object_or_404(project_model, pk=query_project)
            obj.project = project
            obj.save()  # Need save here to set more attrs
            if project.task:
                obj.task = project.task
        obj.save()
