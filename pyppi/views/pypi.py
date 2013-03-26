import logging
from django.contrib.auth import login
from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from pyppi.http import parse_distutils_request, login_basic_auth
from django.views.generic import RedirectView
from pyppi.views import IndexView, ReleaseIndex
from pyppi.views.distutils import RegisterView, UploadView, ClassifierView
from pyppi.views.xmlrpc import parse_xmlrpc_request

__all__ = ['XmlRpcRoot']

log = logging.getLogger(__name__)


class XmlRpcRoot(RedirectView):
    permanent = False
    fallback_view = IndexView

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """ Root view of the package index, handle incoming actions from distutils
        or redirect to a more user friendly view """
        if not request.user.is_authenticated():
            user = login_basic_auth(request)
            if user:
                login(request, user)

        if request.method == 'POST':
            if request.META['CONTENT_TYPE'] == 'text/xml':
                log.debug('XMLRPC request received')
                return parse_xmlrpc_request(request)
            log.debug('Distutils request received')
            parse_distutils_request(request)
            action = request.POST.get(':action', '')
        else:
            action = request.GET.get(':action', '')

        if action == 'submit':
            return RegisterView.as_view()(request, *args, **kwargs)
        elif action == 'file_upload':
            return UploadView.as_view()(request, *args, **kwargs)
        elif action == 'list_classifiers':
            return ClassifierView.as_view()(request, *args, **kwargs)
        elif action == '':
            return ReleaseIndex.as_view()(request, *args, **kwargs)
        else:
            log.error('Invalid action encountered: `%s`', action)
            return HttpResponseNotAllowed(action)

# @csrf_exempt
# def root(request, fallback_view=None, **kwargs):
#     """ Root view of the package index, handle incoming actions from distutils
#     or redirect to a more user friendly view """
#     if request.method == 'POST':
#         if request.META['CONTENT_TYPE'] == 'text/xml':
#             log.debug('XMLRPC request received')
#             return parse_xmlrpc_request(request)
#         log.debug('Distutils request received')
#         parse_distutils_request(request)
#         action = request.POST.get(':action','')
#     else:
#         action = request.GET.get(':action','')
#
#     if not action:
#         log.debug('No action in root view')
#         if fallback_view is None:
#             fallback_view = settings.DJANGOPYPI_FALLBACK_VIEW
#         return fallback_view(request, **kwargs)
#
#     if not action in settings.DJANGOPYPI_ACTION_VIEWS:
#         log.error('Invalid action encountered: %s' % (action,))
#         return HttpResponseNotAllowed(settings.DJANGOPYPI_ACTION_VIEW.keys())
#
#     log.debug('Applying configured action view for %s' % (action,))
#     return settings.DJANGOPYPI_ACTION_VIEWS[action](request, **kwargs)
#
