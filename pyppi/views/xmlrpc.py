import logging
import xmlrpclib
from django.http import HttpResponseNotAllowed, HttpResponse
from django.db.models import Q
from django.utils.importlib import import_module
from pyppi.models import Package, Release
from pyppi.settings import conf

log = logging.getLogger(__name__)


class XMLRPCResponse(HttpResponse):
    """ A wrapper around the base HttpResponse that dumps the output for xmlrpc
    use """

    def __init__(self, params=(), methodresponse=True, *args, **kwargs):
        super(XMLRPCResponse, self).__init__(xmlrpclib.dumps(params,
                                                             methodresponse=methodresponse),
                                             *args, **kwargs)


def parse_xmlrpc_request(request):
    """
    Parse the request and dispatch to the appropriate view
    """
    args, command = xmlrpclib.loads(request.raw_post_data)
    if command in conf.XMLRPC_COMMANDS:
        handler_name = conf.XMLRPC_COMMANDS[command]
        package, name = handler_name.rsplit('.', 1)
        mod = import_module(package)
        handler = getattr(mod, name)
        log.info("Received command {command}. Using handler `{handler}`".format(**locals()))
        return handler(request, *args)
    else:
        log.error('HttpResponseNotAllowed %s', command)
        return HttpResponseNotAllowed(conf.XMLRPC_COMMANDS.keys())


def list_packages(request):
    if request.user.is_authenticated():
        qs = Package.objects.all()
    else:
        qs = Package.objects.public()
    return XMLRPCResponse(params=(list(qs.values_list('name', flat=True)),),
                          content_type='text/xml')


def package_releases(request, package_name, show_hidden=False):
    if request.user.is_authenticated():
        qs = Package.objects.all()
    else:
        qs = Package.objects.public()
    try:
        return XMLRPCResponse(params=(list(
            qs.get(name=package_name).releases.filter(hidden=show_hidden).values_list('version', flat=True)),))
    except Package.DoesNotExist:
        return XMLRPCResponse(params=([],))


def release_urls(request, package_name, version):
    base_url = '%s://%s' % (request.is_secure() and 'https' or 'http',
                            request.get_host())
    dists = []
    try:
        for dist in Package.objects.get(name=package_name).releases.get(version=version).distributions.all():
            dists.append({
                'url': '%s%s' % (base_url, dist.get_absolute_url()),
                'packagetype': dist.filetype,
                'filename': dist.filename,
                'size': dist.content.size,
                'md5_digest': dist.md5_digest,
                'downloads': 0,
                'has_sig': len(dist.signature) > 0,
                'python_version': dist.pyversion,
                'comment_text': dist.comment
            })
    except (Package.DoesNotExist, Release.DoesNotExist):
        pass

    return XMLRPCResponse(params=(dists,))


def release_data(request, package_name, version):
    output = {
        'name': '',
        'version': '',
        'stable_version': '',
        'author': '',
        'author_email': '',
        'maintainer': '',
        'maintainer_email': '',
        'home_page': '',
        'license': '',
        'summary': '',
        'description': '',
        'keywords': '',
        'platform': '',
        'download_url': '',
        'classifiers': '',
        'requires': '',
        'requires_dist': '',
        'provides': '',
        'provides_dist': '',
        'requires_external': '',
        'requires_python': '',
        'obsoletes': '',
        'obsoletes_dist': '',
        'project_url': '',
    }
    try:
        release = Package.objects.get(name=package_name).releases.get(version=version)
        output.update({'name': package_name, 'version': version, })
        output.update(release.package_info)
    except (Package.DoesNotExist, Release.DoesNotExist):
        pass

    return XMLRPCResponse(params=(output,))


def search(request, spec, operator='or'):
    """
    search(spec[, operator])

    Search the package database using the indicated search spec.
    The spec may include any of the keywords described in the above list (except 'stable_version' and 'classifiers'), for example: {'description': 'spam'} will search description fields. Within the spec, a field's value can be a string or a list of strings (the values within the list are combined with an OR), for example: {'name': ['foo', 'bar']}. Valid keys for the spec dict are listed here. Invalid keys are ignored:
    name
    version
    author
    author_email
    maintainer
    maintainer_email
    home_page
    license
    summary
    description
    keywords
    platform
    download_url
    Arguments for different fields are combined using either "and" (the default) or "or". Example: search({'name': 'foo', 'description': 'bar'}, 'or'). The results are returned as a list of dicts {'name': package name, 'version': package release version, 'summary': package release summary}

    changelog(since)

    Retrieve a list of four-tuples (name, version, timestamp, action) since the given timestamp. All timestamps are UTC values. The argument is a UTC integer seconds since the epoch.
    """
    try:
        if request.user.is_authenticated():
            qs = Package.objects.all()
        else:
            qs = Package.objects.public()

        queries = [Q(name__contains=name) for name in spec['name']]
        query = queries.pop()
        for item in queries:
            query |= item

        result = []
        for p in qs.filter(query):
            result.append({
                '_pypi_ordering': 0,
                'name': str(p.name),
                'version': str(p.latest.version) if p.latest else 'not released',
                'summary': str(p.latest.summary) if p.latest else '',
            })
    except Exception as e:
        log.error(e)
        raise
    return XMLRPCResponse(params=(result,))


def changelog(since):
    output = {
        'name': '',
        'version': '',
        'timestamp': '',
        'action': '',
    }
    return XMLRPCResponse(params=(output,))


def ratings(request, name, version, since):
    return XMLRPCResponse(params=([],))


XMLRPC_COMMANDS = {
    'list_packages': list_packages,
    'package_releases': package_releases,
    'release_urls': release_urls,
    'release_data': release_data,
    'search': search,
    #'changelog': xmlrpc.changelog, Not done yet
    #'ratings': xmlrpc.ratings, Not done yet
}
