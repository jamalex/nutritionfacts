nanobox console nutritionfacts web.main

python manage.py shell

from nutritionfacts.models import *
Pingback.objects.values("mode").distinct()

len(sorted(IPLocation.objects.filter(pingback__mode="").annotate(pingback_count=Count("pingback")).filter(pingback_count__gt=5).values_list("pingback_count", flat=True)))


from nutritionfacts.models import *
from django.db.models import Count
ips = IPLocation.objects.filter(pingback__mode="").exclude(host__contains="ucsd.edu").exclude(host__contains="san.res.rr.com")
results = ips.values("country_name").annotate(count=Count("pingback__instance_id", distinct=True))
total_count = 0
total_countries = 0
for count, country in reversed(sorted([(result["count"], result["country_name"]) for result in results])):
    if country:
        print(count, "\t", country)
        total_count += count
        total_countries += 1
print("")
print("Total installations:", total_count)
print("Total countries:", total_countries)

Pingback.objects.filter(mode="").values("instance_id").distinct().annotate(Count("id"))




[sorted(set([(p.instance_id[:5], p.saved_at.year, p.saved_at.month, p.saved_at.day, p.platform) for p in ip.pingback_set.filter(mode__gt="", saved_at__year=2018)])) for ip in IPLocation.objects.filter(pin
gback__saved_at__month=2, pingback__mode="", host__contains="ucsd").distinct()]



from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2017, 12, 1)
end_date = date(2018, 3, 25)
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%Y-%m-%d") + "," + str(Pingback.objects.filter(mode="", saved_at__lte=single_date).values("instance_id").distinct().count()))


    
# First timestamp for each Instance ID 
Pingback.objects.filter(kolibri_version="0.7.0").values("instance_id").distinct().annotate(first_seen=Min("saved_at"))        


# how many DB clones?
Pingback.objects.filter(mode="").values("database_id", "instance_id").distinct().annotate(Count("instance_id")).order_by("-instance_id__count").values_list("instance_id__count", "database_id").distinct()
