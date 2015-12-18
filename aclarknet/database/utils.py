def class_name_pk(self):
    """

    Django Admin object names based on class and pk, e.g.:

    client-1
    client-2
    client-3
    """
    return '-'.join([self.__class__.__name__.lower(), str(self.pk)])


def entries_total(queryset):
    entries = {}
    running_total = 0
    for entry in queryset:
        entries[entry] = {}
        entries[entry]['notes'] = entry.notes
        hours = entry.hours
        entries[entry]['hours'] = hours
        if entry.task:
            rate = entry.task.rate
            entries[entry]['rate'] = rate
            total = float(rate) * float(hours.total_seconds() / 60)
            entries[entry]['total'] = total
            running_total += total
    return entries, running_total
