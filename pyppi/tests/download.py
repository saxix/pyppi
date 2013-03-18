import base64
from contextlib import contextmanager
from django_webtest import WebTest
from pyppi.models import KnownHost
from pyppi.tests import BaseTestMixin
from pyppi.tests.util import user_add_permission


class DistUtilsDownloadTestCase(BaseTestMixin, WebTest):

    @contextmanager
    def basic_auth(self):
        self.auth_password = base64.encodestring('%s:aa%s' % (self.user.username, self.password)).strip()
        old_env, self.app.extra_environ = self.app.extra_environ, {
            'AUTH_TYPE': 'Basic',
            'HTTP_AUTHORIZATION': 'Basic {}'.format(self.auth_password),
            'REMOTE_USER': self.user.username}
        yield
        self.auth_password = None
        self.app.extra_environ = old_env

    def test_needs_valid_user(self):
        res = self.app.get('/simple/', expect_errors=True)
        assert res.status_code == 401

    # def test_user_need_permission_to_download(self):
    #     target = '/simple/%s/' % self.package.name
    #     with self.basic_auth():
    #         res = self.app.get(target, expect_errors=True)
    #         self.assertEqual(res.status_code, 403)

    # def test_ip_restrictions(self):
    #     target = '/simple/%s/' % self.package.name
    #     with user_add_permission(self.user, ['pyppi.download_package'], self.package,
    #                              limit_from='192.168.10.1'):
    #         with self.basic_auth():
    #             res = self.app.get(target, expect_errors=True)
    #             self.assertEqual(res.status_code, 403)

    def test_access_granted(self):
        target = '/simple/%s/' % self.package.name
        with user_add_permission(self.user, ['pyppi.download_package'], self.package,
                                 limit_from='127.0.0.1'):
            with self.basic_auth():
                self.app.get(target)

    def test_known_host(self):
        target = '/simple/%s/' % self.package.name
        host = KnownHost.objects.create(ip='127.0.0.1', description='localhost')
        host.packages.add(self.package)
        self.app.get(target)

    def test_public(self):
        target = '/simple/%s/' % self.package.name
        host = KnownHost.objects.create(ip='127.0.0.1', description='localhost')
        host.packages.add(self.package)
        self.app.get(target)
