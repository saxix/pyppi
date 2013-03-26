# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from pyppi.models import Release
from pyppi.views.base import RedirToMirrorMixin, BasicAuthMixin


__all__ = ['ReleaseIndex', 'ReleaseDetail', 'ReleaseUpload']


class ReleaseIndex(ListView):
    template_name = 'pyppi/release_list.html'
    queryset = Release.objects.filter(hidden=False)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return super(ReleaseIndex, self).get_queryset()
        return Release.objects.public(hidden=False)


class ReleaseDetail(RedirToMirrorMixin, BasicAuthMixin, DetailView):
    template_name = 'pyppi/release_detail.html'
    queryset = Release.objects.filter(hidden=False)
    pk_url_kwarg = 'package'

    def get_object(self, queryset=None):
        package = self.kwargs['package']
        version = self.kwargs['version']
        return self.queryset.get(package__name=package, version=version)


class ReleaseDoapView(ReleaseDetail):
    template_name = 'pyppi/release_doap.xml'


class ReleaseUpload(UpdateView):
    template_name = 'pyppi/release_upload_file.html'
