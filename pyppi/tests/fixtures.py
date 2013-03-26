import os
import StringIO
import tarfile
import hashlib
from django.contrib.auth.models import User
from pyppi.models import Package, Release, Distribution
from django_dynamic_fixture import G


def user_factory(password, **kwargs):
    user = G(User, **kwargs)
    user.set_password(password)
    user.save()
    return user


def package_factory(**kwargs):
    params = dict(visibility=Package.VISIBLE_PERM,
                  access=Package.VISIBLE_PERM)
    params.update(kwargs)
    return G(Package, **params)


def release_factory(package, **kwargs):
    params = dict(version='1.0')
    params.update(kwargs)

    meta = dict({'author': ['sax'],
                 'maintainers': ['sax'],
                 'license': ['BSD'],
                 'classifiers': ['Environment :: Web Environment'],
                 'description': 'package1 is ...',
                 'home_page': ['BSD']})
    package_info = kwargs.pop('package_info', {})
    package_info.update(meta)

    return G(Release, package=package, package_info=package_info, **params)


def distro_factory(release):
    distro_filename = "{0.package.name}-{0.version}.tar.gz".format(release)
    dummy_file, md5 = create_fake_download(distro_filename)
    return G(Distribution, release=release,
             md5_digest=md5,
             content=dummy_file)


def create_fake_download(filename):
    f = Distribution._meta.get_field('content')
    base = f.storage.location
    # base = os.path.abspath(env.base_path)
    if not os.path.isdir(os.path.join(base, f.upload_to)):
        os.mkdir(os.path.join(base, f.upload_to))

    filename = os.path.join(f.upload_to, filename)
    target = os.path.join(base, filename)
    tar = tarfile.open(target, 'w:gz')
    string = StringIO.StringIO()
    string.write("#!python")
    string.seek(0)
    info = tarfile.TarInfo(name="setup.py")
    info.size = len(string.buf)
    tar.addfile(tarinfo=info, fileobj=string)
    tar.close()
    md5 = hashlib.md5(open(target, 'r').read())
    return filename, md5
