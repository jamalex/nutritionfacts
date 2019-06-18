nanobox console nutritionfacts web.main

./manage.py shell_plus

Pingback.objects.values("mode").distinct()

len(sorted(IPLocation.objects.filter(pingback__mode="").annotate(pingback_count=Count("pingback")).filter(pingback_count__gt=5).values_list("pingback_count", flat=True)))


# total installations and total countries
ips = IPLocation.objects.filter(pingbacks__mode="")
results = ips.values("country_name").annotate(count=Count("pingbacks__instance_id", distinct=True))
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



# How many users?
FacilityStatistics.objects.filter(pingback__mode="").values("facility_id").distinct().annotate(Max("learners_count")).aggregate(Sum("learners_count__max"))

sorted(FacilityStatistics.objects.filter(pingback__mode="").values("facility_id").distinct().annotate(Max("sess_user_count"), Max("learners_count"), Max("sess_anon_count")).values_list("learners_count__max", "sess_user_count__max", "sess_anon_count__max", "pingback__ip__country_name"))


# how many per country for a particular day?
Instance.objects.filter(first_seen__year=2019, first_seen__month=1, first_seen__day=4, last_mode="").values("pingbacks__ip__country_name").order_by("pingbacks__ip__country_name").annotate(count=Count("instance_id", distinct=True)).order_by("-count")

Instance.objects.filter(first_seen__year=2019, first_seen__month=1, first_seen__day=4, last_mode="", pingbacks__ip__country_name="Nepal").values("pingbacks__ip_id")



# most popular channels based on what's loaded (not based on what's viewed)
channelstats = ChannelStatistics.objects.filter(pingback__mode="", storage__gt=0)
counts = channelstats.values("channel_id").annotate(Count("pingback__instance_id", distinct=True)).order_by("-pingback__instance_id__count")
print("from contentcuration.models import *")
for channel_id, count in counts.values_list("channel_id", "pingback__instance_id__count"):
	print("channel = Channel.objects.get(id__startswith='{}'); print channel.id, u'\\t', {}, u'\\t', channel.name.encode('utf-8'); ".format(channel_id, count), end="")
# (then paste the results into a Studio shell)


def mean(x):
    return sum(x) / float(len(x))

facilitystats = FacilityStatistics.objects.filter(pingback__mode="")

# average number of registered learners per pinging facility
mean(sorted(facilitystats.values("facility_id").annotate(Max("learners_count")).values_list("learners_count__max", flat=True)))

# average number of anonymous content sessions per pinging facility
mean(sorted(facilitystats.values("facility_id").annotate(Max("sess_anon_count")).values_list("sess_anon_count__max", flat=True)))

