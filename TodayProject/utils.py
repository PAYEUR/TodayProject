from django.contrib.sites.models import Site


def make_key_per_site(key, key_prefix, version):
    site_id = ''
    try:
        site = Site.objects.get_current()
        site_id = site['id']
    except:
        pass

    return ':'.join([key_prefix, site_id, str(version), key])
