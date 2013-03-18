# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
import re
# import shutil
import tempfile
import logging
from pyppi.models import PlatformName, DistributionType, Package

logger = logging.getLogger(__name__)


def user_can_download(request, distro):
    user = request.user
    if distro.release.package.access == Package.VISIBLE_ALL:
        logger.debug('Public package `{distro.release.package}`'.format(**locals()))
        return True
    if user.is_authenticated() and distro.release.package.access == Package.VISIBLE_AUTH:
        logger.debug('Protected package `{distro.release.package}`'.format(**locals()))
        has_perm = True
    else:
        has_perm = user.has_perm('pyppi.download_package') or user.has_perm('pyppi.download_package',
                                                                            distro.release.package)

    from_ip = get_client_ip(request)
    if user.iprestrictions.filter(only_allowed_from=from_ip).exists():
        has_perm = False

    return has_perm

    # return has_perm


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_platform_from_filename(uploaded):
    filename_mo = re.match(
        r'^(?P<package_name>[\w.]+)-(?P<version>[\w.]+)-py(?P<python_version>\d+\.\d+)-(?P<platform_key>[\w.-]+)$',
        os.path.splitext(uploaded.name)[0])
    if filename_mo is None:
        return None

    platform_key = filename_mo.groupdict()['platform_key']
    platform, created = PlatformName.objects.get_or_create(key=platform_key)
    if created:
        platform.name = platform.key
        platform.save()

    return platform


def get_distribution_type(filetype):
    filetype, created = DistributionType.objects.get_or_create(key=filetype)
    if created:
        filetype.name = filetype.key
        filetype.save()
    return filetype


@contextmanager
def tempdir():
    """Simple context that provides a temporary directory that is deleted
    when the context is exited."""
    d = tempfile.mkdtemp(".tmp", "pyppi.")
    yield d
    rmtree(d)


def mktree(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if not newdir:
        raise ValueError('mktree needs a valid pathname as argument')
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired "
                      "dir, '%s', already exists." % newdir)
    else:
        os.makedirs(newdir)


def rmtree(d):
    for path in (os.path.join(d, f) for f in os.listdir(d)):
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.unlink(path)
    os.rmdir(d)
