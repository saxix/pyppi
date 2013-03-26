# -*- coding: utf-8 -*-
from django.core.management.base import LabelCommand
from setuptools.package_index import PackageIndex
from pyppi.util import tempdir


class XPackageIndex(PackageIndex):
    pass


class Command(LabelCommand):
    args = ''

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle_label(self, url, **options):
        with tempdir():
            pypi = XPackageIndex(url)
            pypi.process_url(pypi.index_url, False)
            print pypi.scanned_urls
            print pypi.fetched_urls
            print pypi.package_pages
            print pypi.to_scan

            # path = pypi.download(label, tmp)
            # if path:
            #     self._save_package(path, **options)
            # else:
            #     print "Could not add %s. Not found." % label

            #
