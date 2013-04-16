# -*- coding: utf-8 -*-
import os
import urlparse
import logging
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views import static
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from pyppi.http import login_basic_auth
from pyppi.models import Package, Release, Distribution
from pyppi.util import user_can_download
from pyppi.views.base import basicauth_required

__all__ = ['IndexView', 'LoginView', 'static_serve', 'distro_serve', 'basicauth_required']

logger = logging.getLogger(__name__)


def distro_serve(request, path, document_root=None, show_indexes=False):
    filename = os.path.basename(path)
    distro = Distribution.objects.get(content=path)
    if not request.user.is_authenticated():
        user = login_basic_auth(request)
        if user:
            login(request, user)

    logger.debug(
        "User `{0.user}` dowdloads distro `{1}` of package {2}".format(request, filename, distro.release.package))

    if user_can_download(request, distro):
        logger.debug("User `{0.user}` download distro `{1}` of package {2}".format(request, filename,
                                                                                   distro.release.package))
        return static.serve(request, path, document_root)

    logger.error("User `{0.user}` cannot access to distro `{1}` of package {2}".format(request, filename,
                                                                                       distro.release.package))
    return HttpResponseForbidden()


def static_serve(request, path, document_root=None, show_indexes=False):
    # only used by tests. In production should be intercepted by ngnix
    return static.serve(request, path, document_root, show_indexes)


class IndexView(TemplateView):
    template_name = 'pyppi/index.html'

    def get_context_data(self, **kwargs):
        try:
            if not self.request.user.is_authenticated():
                qs = Package.objects.public()
            else:
                qs = Package.objects.all()
            package = qs.latest('releases__created')
        except Package.DoesNotExist:
            package = None

        try:
            if not self.request.user.is_authenticated():
                qs = Release.objects.public()
            else:
                qs = Release.objects.all()
            release = qs.latest('created')
            # release = Release.objects.public().latest('created')
        except Release.DoesNotExist:
            release = None

        return {
            'package': package,
            'release': release,
        }


class LoginView(FormView):
    """
    This is a class based version of django.contrib.auth.views.login.

    Usage:
        in urls.py:
            url(r'^login/$',
                AuthenticationView.as_view(
                    form_class=MyCustomAuthFormClass,
                    success_url='/my/custom/success/url/),
                name="login"),

    """
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'registration/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in AuthenticationForm.is_valid()). So now we
        can log him in.
        """
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')

        netloc = urlparse.urlparse(redirect_to)[1]
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        # Security check -- don't allow redirection to a different host.
        elif netloc and netloc != self.request.get_host():
            redirect_to = settings.LOGIN_REDIRECT_URL
        return redirect_to

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(), but adds test cookie stuff
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.post(), but adds test cookie stuff
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)


class LoginRequiredMixin(object):
    @method_decorator(basicauth_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)




