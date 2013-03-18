"""
Management command for adding a package to the repository. Supposed to be the
equivelant of calling easy_install, but the install target is the chishop.
"""

from __future__ import with_statement
import os
from django.db import transaction
import pkginfo

from django.core.files.base import File
from django.core.management.base import LabelCommand
from optparse import make_option

from setuptools.package_index import PackageIndex
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDict
from pyppi.models import Package, Release, Classifier
from pyppi.storage import FileExistsError
from pyppi.util import get_distribution_type, tempdir


class Command(LabelCommand):
    option_list = LabelCommand.option_list + (
        make_option("-o", "--owner",
                    help="foce package owner to OWNER",
                    metavar="OWNER", default=None),
        make_option("-f", "--fallback-owner",
                    dest='fallback_owner',
                    help="default packages owner if not present",
                    metavar="OWNER", default=None),
        make_option("-i", "--index",
                    dest='index',
                    help="Pypi site url",
                    metavar="URL", default='http://pypi.python.org/simple'),
        make_option("--visibility",
                    type="choice",
                    choices=map(str, dict(Package.VISIBILITY).keys()),
                    help="set package visibility; %s" % r", ".join("%s=%s" % (a, b) for a, b in Package.VISIBILITY),
                    metavar="VISIBILITY",
                    default=Package.VISIBLE_ALL),

    )
    help = """Add one or more packages to the repository. Each argument can
be a package name or a URL to an archive or egg. Package names honour
the same rules as easy_install with regard to indicating versions etc.

If a version of the package exists, but is older than what we want to install,
the owner remains the same.

For new packages there needs to be an owner. If the --owner option is present
we use that value. If not, we try to match the maintainer of the package, form
the metadata, with a user in out database, based on the If it's a new package
and the maintainer emailmatches someone in our user list, we use that. If not,
the package can not be
added"""

    def __init__(self, *args, **kwargs):
        LabelCommand.__init__(self, *args, **kwargs)

    def handle_label(self, label, **options):
        with tempdir() as tmp:
            self.pypi = PackageIndex(options['index'])
            path = self.pypi.download(label, tmp)
            if path:
                self._save_package(path, **options)
            else:
                print "Could not add %s. Not found." % label

    @transaction.commit_on_success
    def _save_package(self, path, **kwargs):
        force_ownerid = kwargs["owner"]
        fallback_ownerid = kwargs["fallback_owner"]
        visibility = kwargs["visibility"]
        if fallback_ownerid:
            try:
                fallback_owner = User.objects.get(username=fallback_ownerid)
            except User.DoesNotExist:
                print "Fallback owner does not exists"
                return

        meta = self._get_meta(path)
        try:
            # can't use get_or_create as that demands there be an owner
            package = Package.objects.get(name=meta.name)
            isnewpackage = False
        except Package.DoesNotExist:
            package = Package(name=meta.name, visibility=visibility)
            isnewpackage = True

        release = package.get_release(meta.version)
        if not isnewpackage and release and release.version == meta.version:
            print "%s-%s already added" % (meta.name, meta.version)
            return

        # algorithm as follows: If owner is given, try to grab user with that
        # username from db. If doesn't exist, bail. If no owner set look at
        # mail address from metadata and try to get that user. If it exists
        # use it. If not, bail.
        owner = None

        if force_ownerid:
            try:
                owner = User.objects.get(username=force_ownerid)
            except User.DoesNotExist:
                print "Forced owner does not exists."
                return
        else:
            try:
                owner = User.objects.get(email=meta.author_email)
            except User.DoesNotExist:
                owner = fallback_owner

        if not owner:
            print "No owner defined. Use --owner to force one"
            return

        # at this point we have metadata and an owner, can safely add it.
        package.save()

        package.owners.add(owner)
        package.maintainers.add(owner)

        for classifier in meta.classifiers:
            package.classifiers.add(Classifier.objects.get_or_create(name=classifier)[0])

        release = Release()
        release.version = meta.version
        release.package = package
        release.metadata_version = meta.metadata_version
        package_info = MultiValueDict()
        package_info.update(meta.__dict__)
        release.package_info = package_info
        release.save()
        try:
            file = File(open(path, "rb"))
            if isinstance(meta, pkginfo.SDist):
                dist = 'sdist'
            elif meta.filename.endswith('.rmp') or meta.filename.endswith('.srmp'):
                dist = 'bdist_rpm'
            elif meta.filename.endswith('.exe'):
                dist = 'bdist_wininst'
            elif meta.filename.endswith('.egg'):
                dist = 'bdist_egg'
            elif meta.filename.endswith('.dmg'):
                dist = 'bdist_dmg'
            else:
                dist = 'bdist_dumb'
            release.distributions.create(content=file,
                                         uploader=owner,
                                         filetype=get_distribution_type(dist))

            print "%s-%s added" % (meta.name, meta.version)
        except FileExistsError as e:
            print e
            transaction.rollback()

    def _get_meta(self, path):
        data = pkginfo.get_metadata(path)
        if data:
            return data
        else:
            print "Couldn't get metadata from %s. Not added to chishop" % os.path.basename(path)
            return None
