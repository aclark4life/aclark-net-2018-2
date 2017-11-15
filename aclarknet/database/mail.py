from django.contrib import messages


def send_mail(context):
    """
    """
    status = True
    request = context['request']
    if status:
        messages.add_message(request, messages.SUCCESS, 'Mail sent!')
    else:
        messages.add_message(request, messages.WARNING, 'Mail not sent!')
