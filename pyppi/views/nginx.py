import os
import logging
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View
from pyppi import models
from pyppi.util import user_can_download
from pyppi.views.base import BasicAuthMixin


logger = logging.getLogger(__name__)


def find_package(name, parts):
    pass


class NginxAccelRedirect(BasicAuthMixin, View):
    http_method_names = ['get']
    redirect_to = '/secure'

    def get(self, request, *args, **kwargs):
        path = self.kwargs['path']

        filename = os.path.basename(path)
        # filename = re.sub("(\.zip|\.tar\.gz|\.tar)$", "", filename)
        # parts = pkg_resources.parse_version(filename)
        distro = models.Distribution.objects.get(content=path)
        logger.debug(
            "User `{0.user}` dowdloads distro `{1}` of package {2}".format(request, filename, distro.release.package))

        if user_can_download(request.user, distro):
            logger.debug("User `{0.user}` download distro `{1}` of package {2}".format(request, filename,
                                                                                       distro.release.package))
            response = HttpResponse()
            response['X-Accel-Redirect'] = "/".join((self.redirect_to, path))
            response['Content-Type'] = ''
            return response
        else:
            logger.error("User `{0.user}` cannot access to distro `{1}` of package {2}".format(request, filename,
                                                                                               distro.release.package))
        return HttpResponseForbidden()


#def basic_auth(request, path=""):
#    logger.debug("{0.user}: `{1}`".format(request, path))
#
#    response = HttpResponse()
#    #    response['X-Accel-Redirect'] = os.path.join('/', 'secure' , path)
#    #    response['Content-Type'] = ''
#    #    return response
#
#
#
#    if 'HTTP_AUTHORIZATION' in request.META:
#        auth = request.META['HTTP_AUTHORIZATION'].split()
#        if len(auth) == 2:
#            if auth[0].lower() == "basic":
#                uname, passwd = base64.b64decode(auth[1]).split(':')
#                user = authenticate(username=uname, password=passwd)
#                if user is not None:
#                    if user.is_active:
#                        login(request, user)
#                        request.user = user
#
#    if request.user.is_authenticated():
#        filename = os.path.basename(path)
#        filename = re.sub("(\.zip|\.tar\.gz|\.tar)$", "", filename)
#        parts = pkg_resources.parse_version(filename)
#
#        logger.debug("{0.user}: `{1}` {2}".format(request, filename, parts))
#
#        if request.user.has_perm('can_download'):
#            response['X-Accel-Redirect'] = os.path.join('/', 'secure', path)
#            response['Content-Type'] = ''
#            return response
#
#    response.status_code = 401
#    response['WWW-Authenticate'] = 'Basic realm="Login Required"'
#    return response
