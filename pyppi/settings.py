class AppSettings(object):
    defaults = {'RELEASE_UPLOAD_TO': 'dists',
                'RELEASE_STORAGE_PATH': None,
                # 'DIST_FILE_TYPES': (('sdist', 'Source'),
                #                     ('bdist_dumb', '"dumb" binary'),
                #                     ('bdist_rpm', 'RPM'),
                #                     ('bdist_wininst', 'MS Windows installer'),
                #                     ('bdist_egg', 'Python Egg'),
                #                     ('bdist_dmg', 'OS X Disk Image')),
                # 'PYTHON_VERSIONS': (('any', 'Any i.e. pure python'),
                #                     ('2.1', '2.1'),
                #                     ('2.2', '2.2'),
                #                     ('2.3', '2.3'),
                #                     ('2.4', '2.4'),
                #                     ('2.5', '2.5'),
                #                     ('2.6', '2.6'),
                #                     ('2.7', '2.7'),
                #                     ('3.0', '3.0'),
                #                     ('3.1', '3.1'),
                #                     ('3.2', '3.2')),
                'ALLOW_VERSION_OVERWRITE': None,
                'METADATA_FIELDS': {'1.0': ('platform', 'summary', 'description', 'keywords', 'home_page',
                                            'author', 'author_email', 'license', ),
                                    '1.1': ('platform', 'supported_platform', 'summary', 'description',
                                            'keywords', 'home_page', 'download_url', 'author', 'author_email',
                                            'license', 'classifier', 'requires', 'provides', 'obsoletes',),
                                    '1.2': ('platform', 'supported_platform', 'summary', 'description',
                                            'keywords', 'home_page', 'download_url', 'author', 'author_email',
                                            'maintainer', 'maintainer_email', 'license', 'classifier',
                                            'requires_dist', 'provides_dist', 'obsoletes_dist',
                                            'requires_python', 'requires_external', 'project_url')},
                'XMLRPC_COMMANDS': {'list_packages': 'pyppi.views.xmlrpc.list_packages',
                                    'package_releases': 'pyppi.views.xmlrpc.package_releases',
                                    'release_urls': 'pyppi.views.xmlrpc.release_urls',
                                    'release_data': 'pyppi.views.xmlrpc.release_data',
                                    'search': 'pyppi.views.xmlrpc.search',
                                    #'changelog': xmlrpc.changelog, Not done yet
                                    #'ratings': xmlrpc.ratings, Not done yet
                                    }}

    def __init__(self):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        prefix = 'PYPPI_'
        from django.conf import settings

        for name, default in self.defaults.iteritems():
            value = getattr(settings, prefix + name, default)
            setattr(self, name, value)
            setattr(settings, prefix + name, value)


conf = AppSettings()

# from django.conf import settings
#
# # This is disabled on pypi.python.org, can be useful if you make mistakes
# if not hasattr(settings,'PYPPI_ALLOW_VERSION_OVERWRITE'):
#     settings.PYPPI_ALLOW_VERSION_OVERWRITE = False
#
# """ The upload_to argument for the file field in releases. This can either be
# a string for a path relative to your media folder or a callable. For more
# information, see http://docs.djangoproject.com/ """
# if not hasattr(settings,'PYPPI_RELEASE_UPLOAD_TO'):
#     settings.PYPPI_RELEASE_UPLOAD_TO = 'dists'
#
# if not hasattr(settings,'PYPPI_OS_NAMES'):
#     settings.PYPPI_OS_NAMES = (
#         ("aix", "AIX"),
#         ("beos", "BeOS"),
#         ("debian", "Debian Linux"),
#         ("dos", "DOS"),
#         ("freebsd", "FreeBSD"),
#         ("hpux", "HP/UX"),
#         ("mac", "Mac System x."),
#         ("macos", "MacOS X"),
#         ("mandrake", "Mandrake Linux"),
#         ("netbsd", "NetBSD"),
#         ("openbsd", "OpenBSD"),
#         ("qnx", "QNX"),
#         ("redhat", "RedHat Linux"),
#         ("solaris", "SUN Solaris"),
#         ("suse", "SuSE Linux"),
#         ("yellowdog", "Yellow Dog Linux"),
#     )
#
# if not hasattr(settings,'PYPPI_ARCHITECTURES'):
#     settings.PYPPI_ARCHITECTURES = (
#         ("alpha", "Alpha"),
#         ("hppa", "HPPA"),
#         ("ix86", "Intel"),
#         ("powerpc", "PowerPC"),
#         ("sparc", "Sparc"),
#         ("ultrasparc", "UltraSparc"),
#     )
#
# if not hasattr(settings,'PYPPI_DIST_FILE_TYPES'):
#     settings.PYPPI_DIST_FILE_TYPES = (
#         ('sdist','Source'),
#         ('bdist_dumb','"dumb" binary'),
#         ('bdist_rpm','RPM'),
#         ('bdist_wininst','MS Windows installer'),
#         ('bdist_egg','Python Egg'),
#         ('bdist_dmg','OS X Disk Image'),
#     )
#
# if not hasattr(settings,'PYPPI_PYTHON_VERSIONS'):
#     settings.PYPPI_PYTHON_VERSIONS = (
#         ('any','Any i.e. pure python'),
#         ('2.1','2.1'),
#         ('2.2','2.2'),
#         ('2.3','2.3'),
#         ('2.4','2.4'),
#         ('2.5','2.5'),
#         ('2.6','2.6'),
#         ('2.7','2.7'),
#         ('3.0','3.0'),
#         ('3.1','3.1'),
#         ('3.2','3.2'),
#     )
#
# if not hasattr(settings, 'PYPPI_`METADATA_FIELDS'):
#     settings.PYPPI_METADATA_FIELDS = {
#         '1.0': ('platform','summary','description','keywords','home_page',
#                 'author','author_email', 'license', ),
#         '1.1': ('platform','supported_platform','summary','description',
#                 'keywords','home_page','download_url','author','author_email',
#                 'license','classifier','requires','provides','obsoletes',),
#         '1.2': ('platform','supported_platform','summary','description',
#                 'keywords','home_page','download_url','author','author_email',
#                 'maintainer','maintainer_email','license','classifier',
#                 'requires_dist','provides_dist','obsoletes_dist',
#                 'requires_python','requires_external','project_url')}
#
# if not hasattr(settings, 'PYPPI_METADATA_FORMS'):
#     from pyppi.forms import Metadata10Form, Metadata11Form, Metadata12Form
#     settings.PYPPI_METADATA_FORMS = {
#         '1.0': Metadata10Form,
#         '1.1': Metadata11Form,
#         '1.2': Metadata12Form}
#
# # if not hasattr(settings, 'PYPPI_FALLBACK_VIEW'):
# #     from djangopypi.views import releases
# #     settings.PYPPI_FALLBACK_VIEW = releases.index
# #
# # if not hasattr(settings,'PYPPI_ACTION_VIEWS'):
# #     from djangopypi.views import distutils
# #
# #     settings.PYPPI_ACTION_VIEWS = {
# #         "file_upload": distutils.register_or_upload, #``sdist`` command
# #         "submit": distutils.register_or_upload, #``register`` command
# #         "list_classifiers": distutils.list_classifiers, #``list_classifiers`` command
# #     }
#
# if not hasattr(settings,'PYPPI_XMLRPC_COMMANDS'):
#     from djangopypi.views import xmlrpc
#
#     settings.PYPPI_XMLRPC_COMMANDS = {
#         'list_packages': xmlrpc.list_packages,
#         'package_releases': xmlrpc.package_releases,
#         'release_urls': xmlrpc.release_urls,
#         'release_data': xmlrpc.release_data,
#         'search': xmlrpc.search, #Not done yet
#         #'changelog': xmlrpc.changelog, Not done yet
#         #'ratings': xmlrpc.ratings, Not done yet
#     }
#
# """ These settings enable proxying of packages that are not in the local index
# to another index, http://pypi.python.org/ by default. This feature is disabled
# by default and can be enabled by setting PYPPI_PROXY_MISSING to True in
# your settings file. """
# if not hasattr(settings, 'PYPPI_PROXY_BASE_URL'):
#     settings.PYPPI_PROXY_BASE_URL = 'http://pypi.python.org'
#
# if not hasattr(settings, 'PYPPI_PROXY_MISSING'):
#     settings.PYPPI_PROXY_MISSING = False
