from logging import getLogger
from django.http import HttpResponse, QueryDict, HttpResponseBadRequest
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.utils.datastructures import MultiValueDict
from django.contrib.auth import authenticate
from pyppi.models import PythonVersion

log = getLogger(__name__)

class HttpResponseNotImplemented(HttpResponse):
    status_code = 501


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, realm):
        HttpResponse.__init__(self)
        self['WWW-Authenticate'] = 'Basic realm="%s"' % realm


def parse_distutils_request(request):
    """ This is being used because the built in request parser that Django uses,
    django.http.multipartparser.MultiPartParser is interperting the POST data
    incorrectly and/or the post data coming from distutils is invalid.

    One portion of this is the end marker: \r\n\r\n (what Django expects)
    versus \n\n (what distutils is sending).
    """
    try:
        sep = request.raw_post_data.splitlines()[1]
    except:
        raise ValueError('Invalid post data')

    request.POST = QueryDict('', mutable=True)
    try:
        request._files = MultiValueDict()
    except OSError:
        pass

    # for part in filter(lambda e: e.strip(), request.raw_post_data.split(sep)):
    for part in [e for e in request.raw_post_data.split(sep) if e.strip()]:
        try:
            header, content = part.lstrip().split('\n', 1)
        except OSError:
            continue

        if content.startswith('\n'):
            content = content[1:]

        if content.endswith('\n'):
            content = content[:-1]

        headers = parse_header(header)

        if "name" not in headers:
            continue

        if "filename" in headers:
            dist = TemporaryUploadedFile(name=headers["filename"],
                                         size=len(content),
                                         content_type="application/gzip",
                                         charset='utf-8')
            dist.write(content)
            dist.seek(0)
            request.FILES.appendlist(headers['name'], dist)
        else:
            request.POST.appendlist(headers["name"], content)
    return


def parse_header(header):
    headers = {}
    # for kvpair in filter(lambda p: p, map(lambda p: p.strip(),header.split(';'))):
    for kvpair in [p.strip() for p in header.split(';')]:
        try:
            key, value = kvpair.split("=", 1)
        except ValueError:
            continue
        headers[key.strip()] = value.strip('"')

    return headers


def login_basic_auth(request):
    authentication = request.META.get("HTTP_AUTHORIZATION")
    if not authentication:
        log.debug('HTTP_AUTHORIZATION not found in header')
        return
    (authmeth, auth) = authentication.split(' ', 1)
    if authmeth.lower() != "basic":
        return
    auth = auth.strip().decode("base64")
    username, password = auth.split(":", 1)
    return authenticate(username=username, password=password)


def get_python_version(pyversion):
    if pyversion == '':
        pyversion = None
    else:
        try:
            major, minor = (int(x) for x in pyversion.split('.'))
        except ValueError:
            raise HttpResponseBadRequest('Invalid Python version number %r' % (pyversion, ))
        pyversion, created = PythonVersion.objects.get_or_create(major=major, minor=minor)
        if created:
            pyversion.save()
    return pyversion
