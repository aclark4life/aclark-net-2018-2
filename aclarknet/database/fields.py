from collections import OrderedDict


def get_fields(items, exclude_fields=[]):
    for item in items:
        fields = item._meta._get_fields()
        item.fields = OrderedDict()
        for field in fields:
            if not field.is_relation and field.name not in exclude_fields:
                field_name = field.name.title().replace('_', ' ')
                value = getattr(item, field.name)
                if value:
                    try:
                        value = value.title()
                    except AttributeError:  # Probably not "regular" field
                        pass
                item.fields[field_name] = value
    return items
