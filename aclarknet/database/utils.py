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
from import_export import widgets
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


def edit(request,
         form_model,
         model,
         url_name,
         template,
         pk=None,
         client=None,
         project=None,
         invoice_amount=None):

    context = {}
    obj = None

    if pk is None:
        form = form_model()
        # Populate time entry form fields with project, client
        # & task values
        if project:
            entry = model(project=project,
                          client=project.client,
                          task=project.task)
            form = form_model(instance=entry)
        # Populate project entry form fields with client value
        if client:
            entry = model(client=client)
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

            if invoice_amount:
                obj.invoice_amount = invoice_amount
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

            return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))

    context['item'] = obj
    context['form'] = form
    return render(request, template, context)


def entries_total(queryset):
    """
    Add estimate and invoice time entries
    """
    entries = {}
    running_total = 0
    for entry in queryset:
        entries[entry] = {}
        hours = entry.hours
        entries[entry]['hours'] = hours
        entries[entry]['notes'] = entry.notes
        entries[entry]['pk'] = entry.pk
        if entry.task:
            rate = entry.task.rate
            entries[entry]['rate'] = rate
            total = float(rate) * float(hours.total_seconds() / 60)
            entries[entry]['total'] = total
            running_total += total
    return entries, running_total


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
    page = request.GET.get('page')
    search = None

    if request.POST:
        search = request.POST.get('search', '')
        for field in fields:
            query.append(Q(**{field + '__icontains': search}))
        results = model.objects.filter(reduce(operator.or_, query))
    else:
        if model.__class__.__name__ == 'Time':
            if request.user.is_staff:
                results = model.objects.all()
            else:
                entries = model.objects.filter(user=request.user)
        else:
            results = model.objects.all()

    if order_by:
        results = results.order_by(order_by)

    if not search:
        results = paginate(results, page)

    return results
