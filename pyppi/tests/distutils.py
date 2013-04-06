import os
from django.conf import settings
import mock
import base64
from contextlib import contextmanager
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from pyppi.models import Release, Distribution, Package
from pyppi.tests.base import BaseTestMixin
from pyppi.tests.util import user_add_permission


class DistUtilsTestCase(BaseTestMixin, WebTest):
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

    def test_dowload_simple(self):
        res = self.app.get('/simple/', expect_errors=True)
        assert res.status_code == 401
        with user_add_permission(self.user, ['pyppi.download_package'], self.package):
            with self.basic_auth():
                res = self.app.get('/simple/')
                res = res.click('package1')
                res = res.click('package1-1.0.tar.gz')
                if 'X-Accel-Redirect' in res.headers:
                    res = res.goto(res.headers['X-Accel-Redirect'])
                assert res['Content-Type'] == 'application/x-tar'

    def test_register(self):
        """
        only allowed user can register
        """
        data = {':action': 'submit',
                'license': 'BSD',
                'name': 'pyppi',
                'version': '1.0',
                'author': 'sax',
                'metadata_version': '1.0',
                'author_email': 's.apostolico@gmail.com'}

        url = reverse('pyppi-release-index')
        with mock.patch('pyppi.views.pypi.parse_distutils_request'):
            resp = self.app.post(url, data, expect_errors=True)
            self.assertEqual(resp.status_code, 401)
            with self.basic_auth():
                resp = self.app.post(url, data, expect_errors=True)
                self.assertEqual(resp.status_code, 403)

                with user_add_permission(self.user, ['pyppi.register_package']):
                    resp = self.app.post(url, data)
                    self.assertEqual(resp.content, 'release registered')
                    assert Package.objects.filter(name='pyppi').exists()
                    assert Release.objects.filter(package__name='pyppi', version='1.0').exists()

    def test_upload(self):
        """
        only allowed user can upload
        """
        data = {':action': 'file_upload',
                'license': 'BSD',
                'name': 'pyppi',
                'version': '1.0',
                'author': 'sax',
                'metadata_version': '1.0',
                'author_email': 's.apostolico@gmail.com'}
        FILENAME = 'pyppi-1.0.tar.gz'
        files = [('content', FILENAME, __file__)]
        url = reverse('pyppi-release-index')
        with mock.patch('pyppi.views.pypi.parse_distutils_request'):
            resp = self.app.post(url, data, upload_files=files, expect_errors=True)
            self.assertEqual(resp.status_code, 401)
            with self.basic_auth():
                resp = self.app.post(url, data, upload_files=files, expect_errors=True)
                self.assertEqual(resp.status_code, 403)

                with user_add_permission(self.user, ['pyppi.upload_package']):
                    resp = self.app.post(url, data, upload_files=files)
                    self.assertEqual(resp.content, 'upload accepted')
                    assert Package.objects.filter(name='pyppi').exists()
                    assert Release.objects.filter(package__name='pyppi', version='1.0').exists()
                    assert Distribution.objects.filter(release__package__name='pyppi',
                                                       release__version='1.0').exists()
                    distro = Distribution.objects.get(release__package__name='pyppi',
                                                      release__version='1.0')

                    full_path = os.path.join(settings.MEDIA_ROOT, distro.content.name)
                    assert os.path.isfile(full_path)

    def test_upload_overwrite(self):
        """
        only allowed user can upload
        """
        data = {':action': 'file_upload',
                'license': 'BSD',
                'name': 'pyppi',
                'version': '1.0',
                'author': 'sax',
                'metadata_version': '1.0',
                'author_email': 's.apostolico@gmail.com'}
        files = [('content', 'pyppi-1.0.tar.gz', __file__)]
        url = reverse('pyppi-release-index')
        with mock.patch('pyppi.views.pypi.parse_distutils_request'):
            with self.basic_auth():
                with user_add_permission(self.user, ['pyppi.upload_package']):
                    resp = self.app.post(url, data, upload_files=files)
                    self.assertEqual(resp.content, 'upload accepted')
                    resp = self.app.post(url, data, upload_files=files, expect_errors=True)
                    self.assertEqual(resp.status_code, 403)
                    with mock.patch('pyppi.settings.conf.ALLOW_VERSION_OVERWRITE', r"\.dev.*$"):
                        resp = self.app.post(url, data, upload_files=files, expect_errors=True)
                        self.assertEqual(resp.status_code, 403)

                    with user_add_permission(self.user, ['pyppi.overwrite_file']):
                        with mock.patch('pyppi.settings.conf.ALLOW_VERSION_OVERWRITE', r'1\..*'):
                            resp = self.app.post(url, data, upload_files=files)
                            self.assertEqual(resp.content, 'upload accepted')

    def test_list_classifiers(self):
        self.app.get('/pypi/?%3Aaction=list_classifiers')


class XmlRpcTestCase(BaseTestMixin, LiveServerTestCase):
    def setUp(self):
        super(XmlRpcTestCase, self).setUp()
        import xmlrpclib
        url = '%s/pypi/' % self.live_server_url
        secure = 'http://%s:%s@%s:%s/pypi/' % (self.username, self.password, self.server_thread.host, self.server_thread.port)
        self.client = xmlrpclib.ServerProxy(url)
        self.secure = xmlrpclib.ServerProxy(secure)

    def test_package_releases(self):
        ret = self.client.package_releases('package1')
        assert ret == [], ret
        ret = self.secure.package_releases('package1')
        assert ret == ['1.0'], ret

    def test_list_packages(self):
        ret = self.client.list_packages()
        assert ret == ['public_package'], ret
        ret = self.secure.list_packages()
        assert ret != ['public_package'], ret

    # def test_package_roles(self):
    #     ret = self.client.package_roles('package1')
    #     assert ret == ['package1', 'package2'], ret

    # def test_user_packages(self):
    #     ret = self.client.user_packages(self.user.username)
    #     assert ret == ['package1', 'package2'], ret

    # def test_release_downloads(self):
    #     ret = self.client.release_downloads('package1', '1.0')
    #     assert ret == ['package1', 'package2'], ret

    # def test_release_urls(self):
    #     ret = self.client.release_urls('package1', '1.0')
    #
    #     assert 'package1.tar.gz#' in ret['url'], ret

    def test_release_data(self):
        ret = self.client.release_data('package1', '1.0')
        assert ret['name'] == 'package1', ret

    # def test_changelog(self):
    #     ret = self.client.changelog(since, with_ids=False) ()
    #     assert ret == ['package1', 'package2'], ret


