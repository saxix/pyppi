# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from haystack.views import basic_search
import pyppi.admin
from pyppi.feeds import ReleaseFeed
from pyppi.views import IndexView, PackageDetail, PackageDetailSimple, PackageListSimple, PackageList, ReleaseDetail, ReleaseIndex, PackageUpdate
from pyppi.views.nginx import NginxAccelRedirect # NOQA
from pyppi.views.pypi import XmlRpcRoot

admin.autodiscover()
pyppi.admin.override()

urlpatterns = patterns(
    "",

    # url(r'^media/(?P<path>.*)', NginxAccelRedirect.as_view(redirect_to='/secure')),
    # url(r"^secure(?P<path>.*)$", static_serve, {"document_root": settings.MEDIA_ROOT}),

    url(r'^users/', include('django.contrib.auth.urls')),

    url(r'^$', IndexView.as_view(), name='pyppi-home'),

    url(r'^search/', login_required(basic_search, login_url=settings.LOGIN_URL),
        {'template': 'pyppi/search_results.html'},
        name='haystack_search'),
    url(r'^rss/$', ReleaseFeed(), name='pyppi-rss'),


    url(r'^packages/$',
        PackageList.as_view(),
        name='pyppi-package-list'),

    url(r'^packages/(?P<package>[\w\d_\.\-]+)/$',
        PackageDetail.as_view(),
        name='pyppi-package'),

    url(r'^packages/(?P<package>[\w\d_\.\-]+)/edit/$',
        login_required(PackageUpdate.as_view(permissions=[])),
        name='pyppi-package-edit'),

    url(r'^simple/$',
        PackageListSimple.as_view(),
        name='pyppi-package-simple'),

    url(r'^simple/(?P<package>[\w\d_\.\-]+)/$',
        PackageDetailSimple.as_view(),
        name='pyppi-package-simple'),

    url(r'^pypi/$', # warning to not add / here. break pypi protocol
        XmlRpcRoot.as_view(),
        name='pyppi-release-index'),

    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/$',
        PackageDetailSimple.as_view(),
        name='pyppi-pypi-package'),

    # url(r'^pypi/', #
    #     XmlRpcRoot.as_view(),
    #     name='pyppi-release-index'),


    # url(r'^pypi/$',
    #     RegisterView.as_view(),
    #     name='pyppi-release-register'),

    # url(r'^simple/(?P<package>[\w\d_\.\-]+)/$',
    #     PackagesDetail.as_view(),
    #     name='djangopypi-package-simple'),


    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/$','packages.details',
    #     name='djangopypi-package'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/rss/$', ReleaseFeed(),
    #     name='djangopypi-package-rss'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/doap.rdf$','packages.doap',
    #     name='djangopypi-package-doap'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/$','packages.manage',
    #     name='djangopypi-package-manage'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/versions/$','packages.manage_versions',
    #     name='djangopypi-package-manage-versions'),
    #

    url(r'^pypi/$',
        ReleaseIndex.as_view(),
        name='pyppi-release-list'),

    url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/$',
        ReleaseDetail.as_view(), name='pyppi-release'),

    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/doap.rdf$',
    #     'releases.doap',name='djangopypi-release-doap'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/manage/$',
    #     'releases.manage',name='djangopypi-release-manage'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/metadata/$',
    #     'releases.manage_metadata',name='djangopypi-release-manage-metadata'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/$',
    #     'releases.manage_files',name='djangopypi-release-manage-files'),
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/upload/$',
    #     'releases.upload_file',name='djangopypi-release-upload-file'),





    # url(r'^pypi/$',ReleasesIndex.as_view(), name='djangopypi-release-index'),
    # url(r'^rss/$', ReleaseFeed(), name='djangopypi-rss'),
    #
    # url(r'^simple/(?P<package>[\w\d_\.\-]+)/$', SimpleDetail.as_view(), name='djangopypi-package-simple'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/$', PackagesDetail.as_view(), name='djangopypi-package'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/rss/$', ReleaseFeed(), name='djangopypi-package-rss'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/$',PackagesManage.as_view(), name='djangopypi-package-manage'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/$', ReleasesDetail.as_view(),name='djangopypi-release'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/upload/$',
    #     ReleasesUpload.as_view(), name='djangopypi-release-upload-file'),
    #
    # url(r'', include("djangopypi.urls")),


    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/doap.rdf$','djangopypi.views.packages.doap',
    #     name='djangopypi-package-doap'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/manage/versions/$', PackagesManageVersions.as_view(),
    #     name='djangopypi-package-manage-versions'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/doap.rdf$',
    #     'djangopypi.views.releases.doap',name='djangopypi-release-doap'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/manage/$', PackagesManage.as_view(),
    #     name='djangopypi-release-manage'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/metadata/$', 'djangopypi.views.releases.manage_metadata',name='djangopypi-release-manage-metadata'),
    #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/$',
    #     'djangopypi.views.releases.manage_files',name='djangopypi-release-manage-files'),
    # #
    # url(r'^pypi/(?P<package>[\w\d_\.\-]+)/(?P<version>[\w\d_\.\-]+)/files/upload/$',
    #     login_required(djangopypi.views.releases.upload_file), name='djangopypi-release-upload-file'),
    #
    #
    # url(r'^search/', login_required(basic_search, login_url=settings.LOGIN_URL), {'template': 'djangopypi/search_results.html'},
    #     name='haystack_search'),

    # Useful to debug production settings
    # url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS[0]}),
)
from .settings import * # NOQA
