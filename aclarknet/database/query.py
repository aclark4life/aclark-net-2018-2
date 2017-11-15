from django.http import HttpResponseRedirect


def set_check_boxes(obj, query_checkbox, ref, app_settings_model):
    model_name = obj._meta.verbose_name
    if (query_checkbox['active'] == 'on'
            or query_checkbox['active'] == 'off'):  # Active
        if query_checkbox['active'] == 'on':
            obj.active = True
            obj.hidden = False
        else:
            obj.active = False
            if model_name == 'note' and app_settings_model:
                app_settings = app_settings_model.get_solo()
                if app_settings.auto_hide:  # Auto-hide
                    obj.hidden = True
    elif (query_checkbox['subscribe'] == 'on'
          or query_checkbox['subscribe'] == 'off'):  # Subscribe
        if query_checkbox['active'] == 'on':
            obj.subscribed = True
        else:
            obj.subscribed = False
    obj.save()
    return HttpResponseRedirect(ref)


def get_query_string(request, key):
    """
    Return calculated values for some query string keys, else return value.
    """
    if key == 'paginated':
        paginated = request.GET.get('paginated')
        if paginated == u'false':
            return False
        else:
            return True
    elif key == 'search' and request.method == 'POST':
        return request.POST.get('search', '')
    elif key == 'costs':  # plot
        costs = request.GET.get('costs')
        if costs:
            costs = costs.split(' ')
        else:
            costs = []
        costs = [i.split(',') for i in costs]
        return costs
    elif key == 'grosses':  # plot
        grosses = request.GET.get('grosses')
        if grosses:
            grosses = grosses.split(' ')
        else:
            grosses = []
        grosses = [i.split(',') for i in grosses]
        return grosses
    elif key == 'nets':  # plot
        nets = request.GET.get('nets')
        if nets:
            nets = nets.split(' ')
        else:
            nets = []
        nets = [i.split(',') for i in nets]
        return nets
    elif key == 'checkbox':
        query_checkbox = {}
        query_checkbox_active = request.POST.get('checkbox-active')
        query_checkbox_subscribe = request.POST.get('checkbox-subscribe')
        condition = (  # if any of these exist
            query_checkbox_active == 'on' or query_checkbox_active == 'off'
            or query_checkbox_subscribe == 'on'
            or query_checkbox_subscribe == 'off')
        query_checkbox['active'] = query_checkbox_active
        query_checkbox['subscribe'] = query_checkbox_subscribe
        query_checkbox['condition'] = condition
        return query_checkbox
    elif key == 'copy':
        return request.POST.get('copy')
    elif key == 'delete':
        return request.POST.get('delete')
    elif key == 'sent':
        return request.POST.get('sent')
    elif key == 'not_sent':
        return request.POST.get('not_sent')
    else:
        return request.GET.get(key)
