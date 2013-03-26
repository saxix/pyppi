# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic import TemplateView
import pyppi.admin
from pyppi.views import static_serve, distro_serve, basicauth_required


admin.autodiscover()
pyppi.admin.override()

urlpatterns = patterns(
    "",

    url(r"^%s(?P<path>.*)$" % settings.MEDIA_URL[1:],
        basicauth_required(distro_serve),
        {"document_root": settings.MEDIA_ROOT, 'show_indexes': False}),

    url(r"^%s(?P<path>.*)$" % settings.STATIC_URL[1:], static_serve,
        {"document_root": settings.STATIC_ROOT, 'show_indexes': True}),

    url(r'^403/$', TemplateView.as_view(template_name='403.html')),
    url(r'^404/$', TemplateView.as_view(template_name='404.html')),
    url(r'^500/$', TemplateView.as_view(template_name='500.html')),
    url(r'^wip/$', TemplateView.as_view(template_name='wip.html')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^users/', include('django.contrib.auth.urls')),
    url(r'^', include('pyppi.urls'))
)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns += staticfiles_urlpatterns()


