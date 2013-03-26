from django.shortcuts import get_object_or_404
from django.contrib.syndication.views import Feed
from pyppi.models import Package, Release


class ReleaseFeed(Feed):
    """ A feed of releases either for the site in general or for a specific
    package. """

    def get_object(self, request, package=None, **kwargs):
        if package:
            return get_object_or_404(Package, name=package)
        return request.build_absolute_uri('/')

    def link(self, obj):
        if isinstance(obj, Package):
            return obj.get_absolute_url()
        return obj

    def title(self, obj):
        if isinstance(obj, Package):
            return u'Releases for %s' % (obj.name,)
        return u'Package index releases'

    def description(self, obj):
        if isinstance(obj, Package):
            return u'Recent releases for the package: %s' % (obj.name,)
        return u'Recent releases on the package index server'

    def items(self, obj):
        if isinstance(obj, Package):
            return obj.releases.filter(hidden=False).order_by('-created')[:25]
        return Release.objects.filter(hidden=False).order_by('-created')[:40]

    def item_description(self, item):
        if isinstance(item, Release):
            if item.summary:
                return item.summary
        return super(ReleaseFeed, self).item_description(item)
