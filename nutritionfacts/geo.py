import functools
import geoip2.database
import geoip2.errors
import socket


@functools.lru_cache(maxsize=None)
def get_reader():
    return geoip2.database.Reader("geoipdata/GeoLite2-City.mmdb")


def get_ip_info(ip):
    socket.setdefaulttimeout(10)
    try:
        host, _, _ = socket.gethostbyaddr(ip)
    except:
        host = ""
    try:
        response = get_reader().city(ip)
        return {
            "city": response.city.name or "",
            "subdivision": response.subdivisions.most_specific.name or "",
            "country_code": response.country.iso_code or "",
            "country_name": response.country.name or "",
            "continent_code": response.continent.code or "",
            "continent_name": response.continent.name or "",
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
            "accuracy_radius": response.location.accuracy_radius,
            "postal_code": response.postal.code or "",
            "time_zone": response.location.time_zone or "",
            "host": host,
        }
    except geoip2.errors.AddressNotFoundError:
        return {"host": host}
