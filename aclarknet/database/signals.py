from .models import Log
from .models import Profile
from .utils import get_geo_ip_data


# https://stackoverflow.com/a/6109366
def login_receiver(sender, user, request, **kwargs):
    geo_ip_data = get_geo_ip_data(request)
    ip_address = request.META.get('HTTP_X_REAL_IP')
    log = Log(entry='%s logged in from %s with IP address %s' %
              (user, geo_ip_data, ip_address))
    log.save()
    Profile.objects.get_or_create(user=user)
