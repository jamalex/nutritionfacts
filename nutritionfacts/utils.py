import json
import re
import semver
import zlib


def load_zipped_json(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return json.loads(data.decode('utf-8'))


def version_matches_range(version, version_range):

    # if no version range is provided, assume we don't have opinions about the version
    if not version_range or version_range == '*':
        return True

    # support having multiple comma-delimited version criteria
    if "," in version_range:
        return all([version_matches_range(version, vrange) for vrange in version_range.split(",")])

    # extract and normalize version strings
    operator, range_version = re.match(r"([<>=!]*)(\d.*)", version_range).groups()
    range_version = normalize_version_to_semver(range_version)
    version = normalize_version_to_semver(version)

    # check whether the version is in the range
    return semver.match(version, operator + range_version)


def normalize_version_to_semver(version):

    initial, dev = re.match(r"(.*?)(\.dev.*)?$", version).groups()

    # clean up after some funny versions we've seen (e.g. 0.8.0-alpha-0)
    initial = initial.split("-")[0].split("+")[0]

    # extract the numeric semver component and the stuff that comes after
    numeric, after = re.match(r"(\d+\.\d+\.\d+)([^\d].*)?", initial).groups()

    # clean up the different variations of the post-numeric component to ease checking
    after = (after or "").strip("-").strip("+").strip(".").split("+")[0]

    # split up the alpha/beta letters from the numbers, to sort numerically not alphabetically
    after_pieces = re.match(r"([a-z])(\d+)", after)
    if after_pieces:
        after = ".".join([piece for piece in after_pieces.groups() if piece])

    # position final releases between alphas, betas, and further dev
    if not dev:
        after = (after + ".c").strip(".")

    # make sure dev versions are sorted nicely relative to one another
    dev = (dev or "").replace("+", ".").replace("-", ".")

    return "{}-{}{}".format(numeric, after, dev).strip("-")
