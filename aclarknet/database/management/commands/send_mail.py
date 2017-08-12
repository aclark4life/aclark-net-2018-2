from django.core.management.base import BaseCommand, CommandError
from aclarknet.database.models import Contact
from aclarknet.database.utils import mail_compose

class Command(BaseCommand):
    help = 'Sends mail'

    def add_arguments(self, parser):
        parser.add_argument('contact_id', nargs='+', type=int)

    def handle(self, *args, **options):
        contact_id = options.get('contact_id')[0]
        contact = Contact.objects.get(pk=contact_id)
        self.stdout.write(self.style.SUCCESS('Got contact "%s"' % contact_id))
