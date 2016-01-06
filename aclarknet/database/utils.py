from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from import_export import widgets
from md5 import md5
import operator


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


def class_name_pk(self):
    """
    Concatenate class name and id
    """
    return '-'.join([self.__class__.__name__.lower(), str(self.pk)])


def dashboard_total(invoices):
    results = OrderedDict()
    gross = 0
    net = 0
    for invoice in invoices:
        results[invoice] = {}
        results[invoice]['subtotal'] = invoice.subtotal
        results[invoice]['amount'] = invoice.amount
        gross += invoice.subtotal
        net += invoice.amount
    return gross, net


def edit(request,
         form_model,
         model,
         url_name,
         template,
         amount=None,
         client=None,
         company=None,
         pk=None,
         paid_amount=None,
         project=None,
         subtotal=None,
         task=None):

    context = {}
    obj = None

    if pk is None:
        form = form_model()
        # Populate time entry form fields with project, client
        # and task values
        if project:
            entry = model(project=project,
                          client=project.client,
                          task=project.task)
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
    else:
        obj = get_object_or_404(model, pk=pk)
        form = form_model(instance=obj)

    if request.method == 'POST':
        if pk is None:
            form = form_model(request.POST)
        else:
            delete = request.POST.get('delete')
            if delete:
                # Decrement invoice counter
                if (obj._meta.verbose_name == 'invoice' and
                        company.invoice_counter):
                    company.invoice_counter -= 1
                    company.save()
                # Decrement estimate counter
                if (obj._meta.verbose_name == 'estimate' and
                        company.estimate_counter):
                    company.estimate_counter -= 1
                    company.save()
                obj.delete()
                return HttpResponseRedirect(reverse(url_name))

            checkbox = request.POST.get('checkbox')
            if checkbox == 'on' or checkbox == 'off':
                if checkbox == 'on':
                    obj.active = True
                else:
                    obj.active = False
                obj.save()
                return HttpResponseRedirect(reverse(url_name))

            if amount and subtotal and paid_amount:
                obj.amount = amount
                obj.subtotal = subtotal
                obj.paid_amount = paid_amount
                obj.save()
                return HttpResponseRedirect(reverse(url_name))
            elif amount and subtotal:
                obj.amount = amount
                obj.subtotal = subtotal
                obj.save()
                return HttpResponseRedirect(reverse(url_name))
            elif amount:
                obj.amount = amount
                obj.save()
                return HttpResponseRedirect(reverse(url_name))

            form = form_model(request.POST, instance=obj)

        if form.is_valid():
            kwargs = {}
            obj = form.save()
            # Assign user to time entry on creation
            if obj.__class__.__name__ == 'Time' and pk is None:
                obj.user = User.objects.get(username=request.user)
                obj.save()
                if project:
                    kwargs['pk'] = project.pk

            # Assign and increment invoice counter
            if (obj._meta.verbose_name == 'invoice' and
                    company.invoice_counter and pk is None):
                company.invoice_counter += 1
                company.save()
                obj.document_id = company.invoice_counter
                obj.save()

            # Assign and increment estimate counter
            if (obj._meta.verbose_name == 'estimate' and
                    company.estimate_counter and pk is None):
                company.estimate_counter += 1
                company.save()
                obj.document_id = company.estimate_counter
                obj.save()

            # Assign client to invoice
            if obj._meta.verbose_name == 'invoice' and obj.project:
                if obj.project.client and not obj.client:
                    obj.client = obj.project.client
                    obj.save()

            return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))

    context['item'] = obj
    context['form'] = form
    return render(request, template, context)


def entries_total(queryset):
    """
    Add estimate and invoice time entries, maybe should be an aggregate
    (https://docs.djangoproject.com/en/1.9/topics/db/aggregation/)
    """

    entries = OrderedDict()

    total = 0
    running_total = 0
    running_total_dev = 0

    for entry in queryset:
        entries[entry] = {}

        hours = entry.hours

        entries[entry]['date'] = entry.date
        entries[entry]['hours'] = hours
        entries[entry]['notes'] = entry.notes
        entries[entry]['pk'] = entry.pk
        entries[entry]['user'] = entry.user

        line_total = 0
        line_total_co = 0
        line_total_dev = 0

        if entry.task:

            rate = entry.task.rate
            entries[entry]['rate'] = rate
            if rate:
                line_total_co = rate * hours

            entries[entry]['line_total_co'] = line_total_co

            running_total += line_total_co

        if entry.user:

            if hasattr(entry.user, 'profile'):
                line_total_dev = entry.user.profile.rate * hours
                entries[entry]['line_total_dev'] = line_total_dev
                running_total_dev += line_total_dev

        line_total = line_total_co - line_total_dev
        entries[entry]['line_total'] = line_total

    total = running_total - running_total_dev

    return entries, running_total, running_total_dev, total


def gravatar_url(email):
    """
    MD5 hash of email address for use with Gravatar
    """
    return settings.GRAVATAR % md5(email.lower()).hexdigest()


def last_month():
    """
    Returns last day of last month
    """
    first = timezone.now().replace(day=1)
    return first - timezone.timedelta(days=1)


def paginate(items, page):
    """
    """
    paginator = Paginator(items, 10, orphans=5)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items


def search(request, model, fields, order_by=None):
    """
    """
    results = []
    query = []
    active = request.GET.get('active')
    page = request.GET.get('page')
    search = None

    if active:
        results = model.objects.filter(active=True)
        return results

    if request.POST:
        search = request.POST.get('search', '')
        for field in fields:
            query.append(Q(**{field + '__icontains': search}))
        results = model.objects.filter(reduce(operator.or_, query))
    else:
        if model._meta.verbose_name == 'time':
            if request.user.is_staff:
                results = model.objects.all()
            else:
                results = model.objects.filter(user=request.user)
        else:
            results = model.objects.all()

    if order_by:
        results = results.order_by(order_by)

    if not search:
        results = paginate(results, page)

    return results
