from hashlib import md5


def get_note_info(note_model):
    note_info = {}
    active = len(note_model.objects.filter(active=True))
    inactive = len(note_model.objects.filter(active=False))
    hidden = len(note_model.objects.filter(hidden=True))
    not_hidden = inactive - hidden
    total = len(note_model.objects.all())
    note_info['active'] = active
    note_info['inactive'] = inactive
    note_info['hidden'] = hidden
    note_info['not_hidden'] = not_hidden
    note_info['total'] = total
    return note_info


def get_recipients(obj):
    """
    Returns first name and email address
    """
    if not obj:
        return []
    model_name = obj._meta.verbose_name
    if model_name == 'contact':
        return [
            (obj.first_name, obj.email),
        ]
    elif model_name == 'estimate':
        return [(i.first_name, i.email) for i in obj.contacts.all()]
    elif model_name == 'newsletter':
        return [(i.first_name, i.email) for i in obj.contacts.all()]
    elif model_name == 'note':
        return [(i.first_name, i.email) for i in obj.contacts.all()]
    elif model_name == 'time':
        return [('Alex', 'aclark@aclark.net')]


def get_setting(request, app_settings_model, setting, page_size=None):
    """
    Allow user to override global setting
    """
    if not request.user.is_authenticated:
        return
    dashboard_override = user_pref = None
    app_settings = app_settings_model.get_solo()
    if setting == 'icon_size':
        if has_profile(request.user):
            user_pref = request.user.profile.icon_size
        if user_pref:
            return user_pref
        else:
            return app_settings.icon_size
    elif setting == 'icon_color':
        if has_profile(request.user):
            user_pref = request.user.profile.icon_color
        if user_pref:
            return user_pref
        else:
            return app_settings.icon_color
    elif setting == 'page_size':
        if has_profile(request.user):
            user_pref = request.user.profile.page_size
        if user_pref:
            return user_pref
        elif page_size:  # View's page_size preference
            return page_size
        else:
            return app_settings.page_size
    elif setting == 'dashboard_choices':
        dashboard_choices = app_settings.dashboard_choices
        dashboard_override = False
        if has_profile(request.user):
            dashboard_override = request.user.profile.dashboard_override
        if has_profile(request.user) and dashboard_override:
            dashboard_choices = request.user.profile.dashboard_choices
        return dashboard_choices
    elif setting == 'exclude_hidden':
        return app_settings.exclude_hidden


def has_profile(user):
    return hasattr(user, 'profile')


def gravatar_url(email):
    """
    MD5 hash of email address for use with Gravatar. Return generic
    if none exists.
    """
    try:
        return gravatar_url % md5(email.lower()).hexdigest()
    except AttributeError:
        # https://stackoverflow.com/a/7585378/185820
        return gravatar_url % md5('db@aclark.net'.encode('utf-8')).hexdigest()
