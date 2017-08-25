from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from aclarknet.database.models import Note as model
from aclarknet.database.utils import mail_compose
from aclarknet.database.utils import mail_recipients
from aclarknet.database.utils import mail_send


class Command(BaseCommand):
    help = 'Mail obj.field to obj => contacts'

    def add_arguments(self, parser):
        parser.add_argument('obj_type')
        parser.add_argument('obj_id')

    def handle(self, *args, **options):
        obj_id = options.get('obj_id')
        obj_type = options.get('obj_type')
        obj = model.objects.get(pk=obj_id)
        recipients = mail_recipients(obj)
        for first_name, email_address in recipients:
            mail_send(
                **mail_compose(
                    obj,
                    first_name=first_name,
                    mail_to=email_address,
                    request=request))
        # if mail_send(**mail_compose(obj)):
        #     self.stdout.write(self.style.SUCCESS('Mail sent!'))
        # else:
        #     self.stdout.write(self.style.SUCCESS('Mail not sent!'))
