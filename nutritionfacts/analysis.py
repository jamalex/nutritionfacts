import collections
import datetime

from django.db.models import Count

from .models import Instance


def region_counts(year=None, quarter=None, months=None, grouping="country"):
	assert grouping in ["country", "continent"]
	instances = Instance.objects.filter(last_mode="")
	if quarter:
		assert not months, "Can't specify both a quarter and a list of months"
		quarter = int(str(quarter).upper().replace("Q", ""))
		months = list(range((quarter - 1) * 3 + 1, quarter * 3 + 1))
	if months:
		assert year, "If you specify quarter or months, must also specify the year"
		instances = instances.filter(first_seen__month__in=months)
	if year:
		instances = instances.filter(first_seen__year=year)
	counts = instances.values("pingbacks__ip__{}_name".format(grouping)).annotate(count=Count("instance_id", distinct=True)).order_by("-count")
	results = collections.OrderedDict()
	for c in counts:
		name = c["pingbacks__ip__{}_name".format(grouping)]
		if name:
			results[name] = c["count"]
	return results

def region_counts_by_quarter(years=None, grouping="country", threshold=50):
	quarters = []
	current_year = datetime.date.today().year
	current_quarter = (datetime.date.today().month - 1) // 3 + 1
	if not years:
		years = range(2018, current_year + 1)
	for year in years:
		quarters += [{"year": year, "quarter": quarter} for quarter in range(1, 5) if year < current_year or quarter <= current_quarter]
	counts = [region_counts(grouping=grouping, **quarter) for quarter in quarters]
	countries = set([name for count in counts for name in count.keys()])
	timecounts = {name: [] for name in countries}
	for count in counts:
		for country in countries:
			timecounts[country].append(count.get(country, 0))
	results = collections.OrderedDict()
	for country, countrycounts in sorted(timecounts.items(), key=lambda item: -sum(item[1])):
		if max(countrycounts) > threshold:
			results[country] = countrycounts
	return ["{year} Q{quarter}".format(**quarter) for quarter in quarters], results
