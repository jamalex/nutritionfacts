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
Instance.objects.filter(first_seen__year=2019, first_seen__month=1, first_seen__day=4, last_mode="").values("pingbacks__ip__country_name").annotate(count=Count("instance_id", distinct=True)).order_by("-count")

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


from nutritionfacts.analysis import *
import io, csv

quarters, countries = region_counts_by_quarter()
s = io.StringIO()
writer = csv.writer(s)
writer.writerow([""] + quarters)
for country, counts in countries.items():
	writer.writerow([country] + counts)
print(s.getvalue())

quarters, continents = region_counts_by_quarter(grouping="continent")
s = io.StringIO()
writer = csv.writer(s)
writer.writerow([""] + quarters)
for continent, counts in continents.items():
	writer.writerow([continent] + counts)
print(s.getvalue())



# check the IPs and times of pingbacks in UK today
for i in Instance.objects.filter(first_seen__year=2020, first_seen__month=2, first_seen__day=24, last_mode="", pingbacks__ip__country_name="United Kingdom"):
    print(i.database_id, i.node_id, i.first_seen, i.pingbacks.first().ip_id)

# check the pingbacks from this IP, and see the interval between them
ot = None
times = []
for p in Pingback.objects.filter(ip_id="90.252.62.102").order_by("saved_at"):
    s = p.statisticspingback_set.all()
    fs = s[0].facilitystatistics_set.count() if s else 0
    cs = s[0].channelstatistics_set.count() if s else 0
    if ot:
        times.append((p.saved_at - ot).seconds)
        print(times[-1])
    print(p.instance.database_id, p.instance.node_id, p.saved_at, fs, cs)
    ot = p.saved_at
times = [t for t in times if t < 1000]
print("New device every {} seconds".format(sum(times) / len(times)))



from collections import defaultdict

# facility stats object for each facility that has the highest number of learners for that facility
all_fstats = FacilityStatistics.objects.filter(pingback__mode="")
largest_fstats = all_fstats.order_by("facility_id", "-learners_count", "-pingback__saved_at").distinct("facility_id")
# total learners:
# sum([fs.learners_count for fs in largest_fstats])


# CALCULATING GENDERS

def get_gender_counts(learners=True):

    # count genders
    counts = defaultdict(int)
    for fstat in largest_fstats:
        gs = fstat.gender_stats_learners if learners else fstat.gender_stats_non_learners
        new_counts = gs.gender_counts if gs else {}
        for key, val in new_counts.items():
            counts[key] += val

    return dict(counts)

lgc = get_gender_counts(learners=True)
print("Learner gender counts:", lgc)
print("Percent female: {}%".format(int(round((100 * lgc["FEMALE"]) / (lgc["FEMALE"] + lgc["MALE"])))))
print("--")
nlgc = get_gender_counts(learners=False)
print("Non-learner gender counts:", nlgc)
print("Percent female: {}%".format(int(round((100 * nlgc["FEMALE"]) / (nlgc["FEMALE"] + nlgc["MALE"])))))



# CALCULATING AGES

from math import erf, sqrt

def phi(x):
    return (1.0 + erf(x / sqrt(2.0))) / 2.0

def zscore(average, standard_deviation, value):
    return (value - average) / (standard_deviation + 0.00001)

def portion_between(average, standard_deviation, lower, upper):
    return phi(zscore(average, standard_deviation, upper)) - phi(zscore(average, standard_deviation, lower))

age_bins = ((0, 18), (18, 24), (25, 34), (35, 44), (45, 54), (55, 64), (65, 100))


def get_age_counts(learners=True, current_year=2020, age_bins=age_bins):

    year_bins = [(current_year - upper, current_year - lower) for lower, upper in age_bins]

    # count birth years
    counts = [0] * len(year_bins)
    for fstat in largest_fstats:
        bys = fstat.birth_year_stats_learners if learners else fstat.birth_year_stats_non_learners
        if not bys or not bys.total_specified:
            continue
        for i, binrange in enumerate(year_bins):
            lower, upper = binrange
            new_count = bys.total_specified * portion_between(bys.average, bys.standard_deviation, lower, upper)
            counts[i] += new_count

    return list(map(int, counts))

lac = get_age_counts(learners=True)
lacsum = sum(lac)
print("Learner age counts:", lac)
for count, age_bin in zip(lac, age_bins):
    print("Learners between {} and {}: {} ({}%)".format(age_bin[0], age_bin[1], count, int(round(100 * count / lacsum))))
print("--")
nlac = get_age_counts(learners=False)
nlacsum = sum(nlac)
print("Non-learner age counts:", nlac)
for count, age_bin in zip(nlac, age_bins):
    print("Non-learners between {} and {}: {} ({}%)".format(age_bin[0], age_bin[1], count, int(round(100 * count / nlacsum))))
