from django.contrib.gis.geoip2 import GeoIP2
geo_ip = GeoIP2()


def get_geo_ip_data(request, ip_address=None):
    if not ip_address:
        # https://stackoverflow.com/a/4581997/185820
        ip_address = request.META.get('HTTP_X_REAL_IP')
    if ip_address:
        return geo_ip.city(ip_address)
