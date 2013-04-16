from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_webtest import WebTest
from pyppi.tests import BaseTestMixin
from pyppi.tests.util import user_add_permission


class WebTestCase(BaseTestMixin, WebTest):

    def test_home(self):
        url = reverse('pyppi-home')
        with user_add_permission(self.user, ['pyppi']):
            self.login()
            res = self.app.get(url, user=self.user)
            res = res.click('Packages')
            self.assertContains(res, _('Package List'))
            res = res.click('package1')
            res = res.click('Releases')
            self.assertContains(res, _('Release List'))

    def test_download(self):
        url = reverse('pyppi-home')
        with user_add_permission(self.user, ['pyppi.download_package']):
            self.login()
            res = self.app.get(url, user=self.username)
            res = res.goto(res.request.url)
            res = res.click('Releases')
            res = res.click('package1-1')
            res = res.click('package1-1.0.tar.gz')

        res = res.goto(res.request.url, expect_errors=True)
        self.assertEqual(res.status_code, 403)

    def test_manage_package(self):
        """
        test authorization for uploaders/downloaders
        """
        self.login()
        url = reverse('pyppi-package-list')

        res = self.app.get(url, user=self.user)
        res = res.click(self.package.name)
        res = res.click('manage')
        form = res.forms[1]
        form['downloaders'] = ['2']
        form['uploaders'] = ['2']
        form['auto_hide'] = 0
        form['classifiers'] = [form['classifiers'].options[0][0]]
        res = form.submit()
        res = res.follow()

        package = res.context['object']
        self.assertFalse(package.auto_hide)
        self.assertSequenceEqual(package.downloaders.values_list('pk', flat=True), [2])
        self.assertSequenceEqual(package.uploaders.values_list('pk', flat=True), [2])

        form = res.forms[1]
        form['downloaders'] = ['1']
        form['uploaders'] = ['1']
        res = form.submit()
        self.assertSequenceEqual(package.downloaders.values_list('pk', flat=True), [1])
        self.assertSequenceEqual(package.uploaders.values_list('pk', flat=True), [1])

    def test_manage_link(self):
        """
         `manage` link should not visible only to package owners
        """
        self.login()
        url = reverse('pyppi-package-list')

        res = self.app.get(url, user=self.user)
        res = res.click(self.user2_package.name)
        self.assertRaises(IndexError, res.click, 'manage')

