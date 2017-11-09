def get_query(request, query):
    """
    Special handling for some query strings
    """
    if query == 'paginated':
        paginated = request.GET.get('paginated')
        if paginated == u'false':
            return False
        else:
            return True
    elif query == 'search' and request.method == 'POST':
        return request.POST.get('search', '')
    elif query == 'costs':  # plot
        costs = request.GET.get('costs')
        if costs:
            costs = costs.split(' ')
        else:
            costs = []
        costs = [i.split(',') for i in costs]
        return costs
    elif query == 'grosses':  # plot
        grosses = request.GET.get('grosses')
        if grosses:
            grosses = grosses.split(' ')
        else:
            grosses = []
        grosses = [i.split(',') for i in grosses]
        return grosses
    elif query == 'nets':  # plot
        nets = request.GET.get('nets')
        if nets:
            nets = nets.split(' ')
        else:
            nets = []
        nets = [i.split(',') for i in nets]
        return nets
    elif query == 'checkbox':
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
