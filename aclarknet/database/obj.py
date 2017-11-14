from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

URL_NAMES = {
    'Settings App': ('settings_app', 'settings_app_edit', ''),
    'Settings Company': ('settings_company', 'settings_company_edit', ''),
    'Settings Contract': ('settings_contract', 'settings_contract_edit', ''),
    'client': ('client_view', 'client_edit', 'client_index'),
    'contact': ('contact_view', 'contact_edit', 'contact_index'),
    'contract': ('contract_view', 'contract_edit', 'contract_index'),
    'estimate': ('estimate_view', 'estimate_edit', 'estimate_index'),
    'file': ('file_view', 'file_edit', 'file_index'),
    'invoice': ('invoice_view', 'invoice_edit', 'invoice_index'),
    'log': ('log_view', 'log_edit', 'log_index'),
    'newsletter': ('newsletter_view', 'newsletter_edit', 'newsletter_index'),
    'note': ('note_view', 'note_edit', 'note_index'),
    'profile': ('user_view', 'user_edit', 'user_index'),
    'project': ('project_view', 'project_edit', 'project_index'),
    'proposal': ('proposal_view', 'proposal_edit', 'proposal_index'),
    'report': ('report_view', 'report_edit', 'report_index'),
    'service': ('', 'service_edit', ''),
    'task': ('task_view', 'task_edit', 'task_index'),
    'time': ('time_view', 'time_edit', 'time_index'),
    'user': ('user_view', 'user_edit', 'user_index'),
}


def get_template_and_url(**kwargs):
    """
    """
    model_name = kwargs.get('model_name')
    page_type = kwargs.get('page_type')
    if page_type == 'view':
        url_name = URL_NAMES[model_name][0]
        template_name = '%s.html' % url_name
        return template_name, url_name
    elif page_type == 'copy':
        url_name = URL_NAMES[model_name][1]
        return url_name
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
        times = time_model.objects.filter(estimate=None, invoice=obj)
    elif model_name == 'project':
        times = time_model.objects.filter(
            invoiced=False, estimate=None, project=obj)
    return times


def obj_copy(obj):
    dup = obj
    dup.pk = None
    dup.save()
    kwargs = {}
    kwargs['pk'] = dup.pk
    model_name = obj._meta.verbose_name
    url_name = get_template_and_url(model_name=model_name, page_type='copy')
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def obj_redir(obj, pk=None):
    """
    Redir after edit, special cases for some objects
    """
    model_name = obj._meta.verbose_name
    template_name, url_name = get_template_and_url(
        model_name=model_name, page_type='view')  # Redir to view
    kwargs = {}
    if pk:  # Exists
        kwargs['pk'] = pk
        if model_name == 'Settings App':  # Special cases for settings
            return HttpResponseRedirect(reverse(url_name))
        elif model_name == 'Settings Company':
            return HttpResponseRedirect(reverse(url_name))
        elif model_name == 'Settings Contract':
            return HttpResponseRedirect(reverse(url_name))
    else:  # New
        if model_name == 'profile':  # One of to create profile for new
            kwargs['pk'] = obj.user.pk  # user
        else:
            kwargs['pk'] = obj.pk
    return HttpResponseRedirect(reverse(url_name, kwargs=kwargs))


def obj_remove(obj):
    model_name = obj._meta.verbose_name
    if model_name == 'time':
        url_name = get_template_and_url(
            model_name=model_name, page_type='home')  # Redir to home
    else:
        url_name = get_template_and_url(
            model_name=model_name, page_type='index')  # Redir to index
    if model_name == 'profile':
        obj.user.delete()
    else:
        obj.delete()
    return HttpResponseRedirect(reverse(url_name))


def obj_sent(obj, ref, invoiced=True):
    """
    Mark time entry as invoiced when invoice sent.
    """
    now = timezone.now()
    for time in obj.time_set.all():
        if invoiced:
            time.invoiced = True
        else:
            time.invoiced = False
        time.save()
    if invoiced:
        obj.last_payment_date = now
    else:
        obj.last_payment_date = None
    obj.save()
    return HttpResponseRedirect(ref)
