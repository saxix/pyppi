from django.test import LiveServerTestCase
from pyppi.tests import BaseTestMixin


class PipTestCase(BaseTestMixin, LiveServerTestCase):
    def setUp(self):
        super(PipTestCase, self).setUp()

        url = self.live_server_url
        basic_auth_url = 'http://%s:%s@%s:%s' % (
            self.username, self.password, self.server_thread.host, self.server_thread.port)

        self.index_url = "%s/pypi/" % url
        self.basic_auth_index_url = "%s/pypi/" % basic_auth_url

        self.simple_url = "%s/simple/" % url
        self.basic_auth_simple_url = "%s/simple/" % basic_auth_url

    def _pip(self, *args, **kw):
        a = list(args)
        if kw.pop('secure', False):
            url = self.basic_auth_index_url
        else:
            url = self.index_url
        a.extend(['--index', url])
        #FIXME: it's not relevant for our tests, but investigate why pip is not able to
        # untar the downloaded files
        return self.env.run('/data/VENV/pyppi/bin/pip', expect_error=True, *a, **kw)

    def test_search(self):
        self.reset_env()
        result = self._pip('search', 'package', '-vvv')
        self.assertEqual(result.stdout, u'public_package            - \n')

    def test_no_download_if_no_auth(self):
        self.reset_env()
        result = self._pip('install',
                           'public_package',
                           '-d', self.env.base_path,
                           '--no-install')
        assert 'public_package-1.0.tar.gz' not in result.files_after.keys()

    def test_priv_download(self):
        self.reset_env()
        result = self._pip('install',
                           'protected_package',
                           '-d', self.env.base_path,
                           '--no-install',
                           secure=True)
        assert 'protected_package-1.0.tar.gz' in result.files_after.keys()

