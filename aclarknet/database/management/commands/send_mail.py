from django.core.management.base import BaseCommand, CommandError
from aclarknet.database.models import Contact
from aclarknet.database.utils import mail_compose
from aclarknet.database.utils import mail_send


class Command(BaseCommand):
    help = 'Sends mail'

    def add_arguments(self, parser):
        parser.add_argument('contact_id', nargs='+', type=int)

    def handle(self, *args, **options):
        contact_id = options.get('contact_id')[0]
        mail_send(**mail_compose(Contact, pk=contact_id))
        self.stdout.write(self.style.SUCCESS('Mail sent!'))
