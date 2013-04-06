class AppSettings(object):
    defaults = {'RELEASE_UPLOAD_TO': 'dists',
                'RELEASE_STORAGE_PATH': None,
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
