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
