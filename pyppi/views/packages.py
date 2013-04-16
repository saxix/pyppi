# -*- coding: utf-8 -*-
import logging
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, ListView, UpdateView, DetailView
import pyppi
from pyppi.forms import PackageForm
from pyppi.models import Package
from pyppi.util import get_user
from pyppi.views.base import BasicAuthMixin, SecuredViewMixin

__all__ = ['PackageList', 'PackageDetail', 'PackageListSimple', 'PackageDetailSimple',
           'PackageUpdate']

log_security = logging.getLogger('security')


# class CheckDownloadPermission(SecuredViewMixin):
#     """A mixin for views that provides them with the selected office."""
#     permissions = ['pyppi.download_package']
#
#     def get_object(self):  # returns selected office and caches the office
#         """The office that is referenced form the url."""
#         package = Package.objects.get(name=self.kwargs['package'])
# ip = get_client_ip(self.request)
# if KnownHost.objects.filter(ip=ip, packages=package).exists():
#     return package
# if not user_can_download(self.request.user, package, ip):
#     log_security.error(msg)
# raise PermissionDenied()

# self.check_perms(self.request, package, True)
# if self.request.user.iprestrictions.exists():
#     if not self.request.user.iprestrictions.filter(only_allowed_from=ip).exists():
#         msg = u'IP Address not allowed {} % ip '.format(ip)
#         log_security.error(msg)
#         raise PermissionDenied()
# return package


class PackageList(SecuredViewMixin, ListView):
    template_name = 'pyppi/package_list.html'
    queryset = Package.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return super(PackageList, self).get_queryset()
        return Package.objects.public()


class PackageDetail(SecuredViewMixin, DetailView):
    template_name = 'pyppi/package_detail.html'
    model = Package
    pk_url_kwarg = 'package'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return super(PackageDetail, self).get_queryset()
        return Package.objects.public()

    def get_context_data(self, **kwargs):
        user = get_user(self.request)
        kwargs['manage_allowed'] = user.packages_owned.filter(pk=self.object.pk).exists()
        return super(PackageDetail, self).get_context_data(**kwargs)


class PackageDoapView(PackageDetail):
    template_name = 'pyppi/package_doap.xml'


class PackageUpdate(SecuredViewMixin, UpdateView):
    template_name = 'pyppi/package_manage.html'
    model = Package
    pk_url_kwarg = 'package'
    form_class = PackageForm

    def get_queryset(self):
        return self.request.user.packages_owned.all()

    def get_initial(self):
        return {
            'downloaders': self.object.downloaders.values_list('pk', flat=True),
            'uploaders': self.object.uploaders.values_list('pk', flat=True)
        }

    def get_success_url(self):
        return reverse('pyppi-package-edit', args=[self.object.name])


# class PackagesManageVersions(BasicAuthMixin, TemplateView):
#     template_name = 'djangopypi/package_manage_versions.html'
#
#     def get(self, request, *args, **kwargs):
#         return djangopypi.views.packages.manage_versions(request, self.kwargs['package'])


class PackageListSimple(BasicAuthMixin, ListView):
    template_name = 'pyppi/package_list_simple.html'
    model = Package


class PackageDetailSimple(BasicAuthMixin, DetailView):
    template_name = 'pyppi/package_detail_simple.html'
    pk_url_kwarg = 'package'
    model = Package


class PackagesManage(BasicAuthMixin, UpdateView):
    template_name = 'pyppi/package_manage.html'
    model = Package
    pk_url_kwarg = 'package'
    form_class = PackageForm

    def get_queryset(self):
        return self.request.user.packages_owned.all()


class PackagesManageVersions(BasicAuthMixin, TemplateView):
    template_name = 'pyppi/package_manage_versions.html'

    def get(self, request, *args, **kwargs):
        return pyppi.views.packages.manage_versions(request, self.kwargs['package'])


# def _mirror_if_not_found(proxy_folder):
#     def decorator(func):
#         def internal(request, package_name):
#             try:
#                 return func(request, package_name)
#             except Http404:
#                 for mirror_site in MirrorSite.objects.filter(enabled=True):
#                     url = '/'.join([mirror_site.url.rstrip('/'), proxy_folder, package_name])
#                     mirror_site.logs.create(action='Redirect to ' + url)
#                     return HttpResponseRedirect(url)
#             raise Http404(u'%s is not a registered package' % (package_name,))
#         return internal
#     return decorator
