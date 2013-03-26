#!/usr/bin/env python
import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

dirname = 'pyppi'

app = __import__(dirname)
app.get_version()
VERSIONMAP = {'final': (app.VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (app.VERSION, 'Development Status :: 4 - Beta'),
              'beta': (app.VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha')}
download_tag, development_status = VERSIONMAP[app.VERSION[3]]


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def scan_dir(target, ):
    for dirpath, dirnames, filenames in os.walk(target):
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'):
                del dirnames[i]
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
    return packages, data_files


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

packages, data_files = scan_dir(dirname)


def process_requirements(filename):
    urls, pkgs = [], []
    with open(filename) as fd:
        for line in fd.read().splitlines():
            line = line.strip()
            if line.startswith('-i'):
                urls.append(line.split()[1])
            elif line.startswith('http://') or line.startswith('https://'):
                urls.append(line)
                pkgs.append(os.path.basename(line))
            elif line.startswith('-f'):
                urls.append(line.split()[1])
            elif line.startswith('-r'):
                include_file = line.split()[1]
                a, b = process_requirements(os.path.join(os.path.dirname(filename), include_file))
                pkgs.extend(a)
                urls.extend(b)
            elif line.startswith('#'):
                pass
            else:
                pkgs.append(line)
    return pkgs, urls


dependencies, dependency_links = process_requirements('pyppi/requirements/defaults.pip')


def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=app.NAME,
    version=app.get_version(),
    url='http://github.com/saxix/pyppi',
    author='sax',
    author_email='s.apostolico@gmail.com',
    keywords='django pypi packaging index',
    license="BSD",
    description="A Django application that emulates the Python Package Index. ",
    long_description=fread("README.txt"),
    install_requires=dependencies,
    dependency_links=dependency_links,
    packages=packages,
    data_files=data_files,
    platforms=['linux'],
    scripts=['pyppi/bin/pyppi', ],
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers'],
)
