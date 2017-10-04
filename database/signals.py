from .models import Log
from .models import Profile
from .utils import get_client_city


# https://stackoverflow.com/a/6109366
def login_receiver(sender, user, request, **kwargs):
    city_data = get_client_city(request)
    log = Log(entry='%s logged in from %s' % (user, city_data))
    log.save()
    Profile.objects.get_or_create(user=user)
