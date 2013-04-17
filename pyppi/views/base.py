# -*- coding: utf-8 -*-
import base64
from functools import wraps
from logging import getLogger
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.utils.decorators import available_attrs, method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from guardian.utils import get_anonymous_user
from pyppi.http import login_basic_auth, HttpResponseUnauthorized
from pyppi.models import KnownHost, MirrorSite
from pyppi.util import get_client_ip

log = getLogger(__name__)
mirror_log = getLogger('pyppi.mirrors')


def basicauth_required(function=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)

            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    if auth[0].lower() == "basic":
                        uname, passwd = base64.b64decode(auth[1]).split(':')
                        if uname.lower() == 'anonymous':
                            user = get_anonymous_user()
                        else:
                            user = authenticate(username=uname, password=passwd)
                        if user is not None and user.is_active:
                            pass
                        else:
                            user = get_anonymous_user()
                        login(request, user)
                        request.user = user
                        return view_func(request, *args, **kwargs)

            return HttpResponseUnauthorized('')

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator

# def to_mirror_if_not_found(proxy_folder, function=None):
#     def decorator(view_func):
#         @wraps(view_func, assigned=available_attrs(view_func))
#         def _wrapped_view(request, *args, **kwargs):
#             try:
#                 return view_func(request, *args, **kwargs)
#             except ObjectDoesNotExist:
#                 for mirror_site in MirrorSite.objects.filter(enabled=True):
#                     url = '/'.join([mirror_site.url.rstrip('/'), request.path])
#                     mirror_site.logs.create(action='Redirect to ' + url)
#                     return HttpResponseRedirect(url)
#             raise Http404(u'%s is not a registered package')
#         return _wrapped_view
#     if function:
#         return decorator(function)
#     return decorator


class LoginRequiredMixin(object):
    @method_decorator(basicauth_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class SecuredViewMixin(object):
    permissions = None


    def check_perms(self, request, obj=None, raise_exception=False):
        assert isinstance(self.permissions, list), 'missing `permissions` attribute in %s' % self.__class__
        user = request.user
        for perm_name in self.permissions:
            if settings.DEBUG:
                if '.' in perm_name:
                    app, perm = perm_name.split('.')
                    assert Permission.objects.filter(codename=perm,
                                                     content_type__app_label=app).exists(), "`%s` is not a registered permission" % perm_name
                else:
                    assert Permission.objects.filter(content_type__app_label=perm_name).exists(), "`%s` is not a registered application" % perm_name

            if not (user.has_perm(perm_name, obj) or user.has_module_perms(perm_name)):
                if obj is not None:
                    access_denied_message = u'[{4}]:User `{0}` has no access to {1} `{2}`:`{3}` permission required'.format(
                        user, obj._meta.verbose_name, obj, perm_name, self.__class__)
                else:
                    access_denied_message = u'[{2}]:User `{0}` has no access here. `{1}` permission required '.format(
                        user, perm_name, self.__class__.__name__)
                log.error(access_denied_message)

                if raise_exception:
                    raise PermissionDenied(access_denied_message)
                return False

        return True


class CheckPermissionMixin(SecuredViewMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.permissions:
            if not self.check_perms(request):
                return HttpResponseForbidden()
        return super(CheckPermissionMixin, self).dispatch(request, *args, **kwargs)


class RedirToMirrorMixin(object):
    def get(self, request, *args, **kwargs):
        try:
            return super(RedirToMirrorMixin, self).get(request, *args, **kwargs)
        except ObjectDoesNotExist:
            for mirror_site in MirrorSite.objects.filter(enabled=True):
                url = ''.join([mirror_site.url.rstrip('/'), request.path])
                mirror_log.info("Package not found. redirecting to %s", url)
                return HttpResponseRedirect(url)
            raise Http404('')


class BasicAuthMixin(object):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            log.info('User `{request.user}` logged in'.format(**locals()))
            return super(BasicAuthMixin, self).dispatch(request, *args, **kwargs)

        # this is a two step authorization
        # here we simply skip the Basic Auth for the known-host
        # see CheckDownloadPermission for the 'package' check
        ip = get_client_ip(request)
        if KnownHost.objects.filter(ip=ip).exists():
            log.info('KnownHost `{ip}` for {request.path}'.format(**locals()))
            return super(BasicAuthMixin, self).dispatch(request, *args, **kwargs)

        user = login_basic_auth(request)

        if not user:
            log.info('Unable to login')
            return HttpResponseUnauthorized('pypi')
        login(request, user)
        if not request.user.is_authenticated():
            return HttpResponseForbidden("Not logged in, or invalid username/password.")
        log.info('User `{user}` logged in'.format(**locals()))
        return super(BasicAuthMixin, self).dispatch(request, *args, **kwargs)


class Wip(TemplateView):
    template_name = 'wip.html'
