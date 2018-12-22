from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.core.urlresolvers import reverse

from topic.models import Occurrence


class DynamicSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Occurrence.objects.all()


class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        urls = ['index',
                'contact',
                'team',
                'CGU',
                'cookies',
                'help_us',
                'tutorial',
                'presentation',
                'charte',
                'explain_categories']

        return ['core:' + url for url in urls]

    def location(self, item):
        return reverse(item)


def sitemaps():
    return {'dynamic': DynamicSitemap,
            'static': StaticSitemap,
            }
