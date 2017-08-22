from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from aclarknet.database.models import Note
from aclarknet.database.utils import mail_compose
from aclarknet.database.utils import mail_send


class Command(BaseCommand):
    help = 'Send note'

    def add_arguments(self, parser):
        parser.add_argument('note_id', nargs='+', type=int)

    def handle(self, *args, **options):
        note_id = options.get('note_id')[0]
        obj = Note.objects.get(pk=note_id)
        mail_send(**mail_compose(obj))
        # if status:
        #     self.stdout.write(self.style.SUCCESS('Mail sent!'))
        # else:
        #     self.stdout.write(self.style.SUCCESS('Mail not sent!'))
