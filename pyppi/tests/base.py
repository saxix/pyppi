import os
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from pyppi.models import Distribution, Package, Classifier
from pyppi.tests.fixtures import distro_factory, package_factory, release_factory, user_factory
from scripttest import TestFileEnvironment

import pyppi
from pyppi.util import mktree

base = os.path.join(os.path.dirname(pyppi.__file__), os.pardir, '~build', 'test-output')
mktree(os.path.dirname(base))
env = TestFileEnvironment(base, capture_temp=True)


class BaseTestMixin(object):
    def setUp(self):
        super(BaseTestMixin, self).setUp()
        self.env = env
        os.chdir(env.base_path)
        self.sett = self.settings(MEDIA_ROOT=self.env.base_path)
        self.sett.enable()

        f = Distribution._meta.get_field('content')
        f.storage.location, self.storage_location = self.env.base_path, f.storage.location

        self.username = 'sax'
        self.password = '123'
        self.user = user_factory(self.password, username=self.username)
        self.user2 = user_factory(self.password)
        G(Group, n=4)

        self.package = package_factory(name='package1', owners=[self.user])
        self.public_package = package_factory(name='public_package', owners=[self.user],
                                              visibility=Package.VISIBLE_ALL,
                                              access=Package.VISIBLE_ALL)
        self.protected_package = package_factory(name='protected_package', owners=[self.user],
                                                 visibility=Package.VISIBLE_AUTH,
                                                 access=Package.VISIBLE_AUTH)

        self.other_package = package_factory(name='package2', owners=[self.user])
        self.user2_package = package_factory(name='user2_package', owners=[self.user2])

        G(Classifier, n=10, shelve=True)
        r = release_factory(self.package)
        r2 = release_factory(self.public_package)
        r3 = release_factory(self.protected_package)
        r4 = release_factory(self.user2_package)

        self.distro = distro_factory(r)
        distro_factory(r2)
        distro_factory(r3)
        distro_factory(r4)

    def tearDown(self):
        super(BaseTestMixin, self).tearDown()
        self.sett.disable()
        f = Distribution._meta.get_field('content')
        f.storage.location = self.storage_location

    def reset_env(self):
        pass

    def login(self):
        res = self.app.get(reverse('login'))
        form = res.forms[1]
        form['username'] = self.username
        form['password'] = self.password
        response = form.submit().follow()
        self.assertEqual(response.context['user'].username, self.username)
