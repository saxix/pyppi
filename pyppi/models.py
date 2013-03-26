import os
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group
from pyppi.fields import PackageInfoField
from pyppi.settings import conf
from pyppi.storage import PyppiStorage


class PythonVersion(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()

    class Meta:
        ordering = ('major', 'minor')
        verbose_name = _(u'python version')
        verbose_name_plural = _(u'python versions')
        unique_together = ('major', 'minor')

    def __unicode__(self):
        return '%s.%s' % (self.major, self.minor)


class PlatformName(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = _(u'platform name')
        verbose_name_plural = _(u'platform names')
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Architecture(models.Model):
    key = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = _(u'architecture')
        verbose_name_plural = _(u'architectures')
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class DistributionType(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = _(u'distribution type')
        verbose_name_plural = _(u'distribution types')
        ordering = ('name', )

    def __unicode__(self):
        return self.name


class Classifier(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

    class Meta:
        verbose_name = _(u"classifier")
        verbose_name_plural = _(u"classifiers")
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class PackageManager(models.Manager):
    def public(self, **kwargs):
        return self.get_query_set().filter(visibility=Package.VISIBLE_ALL)


class Package(models.Model):
    VISIBLE_ALL = 1
    VISIBLE_AUTH = 2
    VISIBLE_PERM = 3

    VISIBILITY = ((VISIBLE_ALL, _('All even not authenticated')),
                  (VISIBLE_AUTH, _('Any authenticated user')),
                  (VISIBLE_PERM, _('User need `download/upload` permission')))

    name = models.CharField(max_length=255, unique=True, primary_key=True,
                            editable=False)
    auto_hide = models.BooleanField(default=True, blank=False)
    allow_comments = models.BooleanField(default=True, blank=False)
    owners = models.ManyToManyField(User, blank=True,
                                    related_name="packages_owned")
    maintainers = models.ManyToManyField(User, blank=True,
                                         related_name="packages_maintained")

    classifiers = models.ManyToManyField(Classifier)
    visibility = models.IntegerField(choices=VISIBILITY, default=VISIBLE_PERM, help_text='Package visibility rule')
    access = models.IntegerField(choices=VISIBILITY, default=VISIBLE_PERM, help_text='Package download rule')

    objects = PackageManager()

    class Meta:
        verbose_name = _(u"package")
        verbose_name_plural = _(u"packages")
        get_latest_by = "releases__latest"
        ordering = ['name', ]
        permissions = (('register_package', 'Can register package'),
                       ('upload_package', 'Can upload package'),
                       ('download_package', 'Can download package'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('pyppi-package', (), {'package': self.name})

    @property
    def latest(self):
        try:
            return self.releases.latest()
        except Release.DoesNotExist:
            return None

    @property
    def downloaders(self):
        return Group.objects.filter(groupobjectpermission__content_type__app_label=self._meta.app_label,
                                    groupobjectpermission__object_pk=self.pk,
                                    groupobjectpermission__permission__codename='download_package')

    @property
    def uploaders(self):
        return Group.objects.filter(groupobjectpermission__content_type__app_label=self._meta.app_label,
                                    groupobjectpermission__object_pk=self.pk,
                                    groupobjectpermission__permission__codename='upload_package')

    def get_release(self, version):
        """Return the release object for version, or None"""
        try:
            return self.releases.get(version=version)
        except Release.DoesNotExist:
            return None


class ReleaseManager(models.Manager):
    def public(self, **kwargs):
        return self.get_query_set().filter(package__visibility=Package.VISIBLE_ALL)


class Release(models.Model):
    package = models.ForeignKey(Package, related_name="releases", editable=False)
    version = models.CharField(max_length=128, editable=False)
    metadata_version = models.CharField(max_length=64, default='1.0')
    package_info = PackageInfoField(blank=False)
    hidden = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = ReleaseManager()

    class Meta:
        verbose_name = _(u"release")
        verbose_name_plural = _(u"releases")
        unique_together = ("package", "version")
        get_latest_by = 'created'
        ordering = ['-created']

    def __unicode__(self):
        return self.release_name

    def save(self, force_insert=False, force_update=False, using=None):
        return super(Release, self).save(force_insert, force_update, using)

    @property
    def release_name(self):
        return u"%s-%s" % (self.package.name, self.version)

    @property
    def summary(self):
        return self.package_info.get('summary', u'')

    @property
    def description(self):
        return self.package_info.get('description', u'')

    @property
    def classifiers(self):
        return self.package_info.getlist('classifier')

    @models.permalink
    def get_absolute_url(self):
        return ('pyppi-release', (), {'package': self.package.name, 'version': self.version})


class Distribution(models.Model):
    release = models.ForeignKey(Release, related_name="distributions",
                                editable=False)
    content = models.FileField(upload_to=conf.RELEASE_UPLOAD_TO,
                               storage=PyppiStorage(conf.RELEASE_STORAGE_PATH))
    md5_digest = models.CharField(max_length=32, blank=True, editable=False)
    filetype = models.ForeignKey(DistributionType, related_name='distributions')
    pyversion = models.ForeignKey(PythonVersion, related_name='distributions', null=True,
                                  help_text='Python version, or None for any version of Python')
    platform = models.ForeignKey(PlatformName, related_name='distributions', null=True,
                                 help_text='Platform name or None if platform agnostic')

    comment = models.CharField(max_length=255, blank=True)
    signature = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    uploader = models.ForeignKey(User, editable=False, blank=True, null=True)

    class Meta:
        verbose_name = _(u"distribution")
        verbose_name_plural = _(u"distributions")
        unique_together = ("release", "filetype", "pyversion")
        permissions = (('overwrite_file', 'Can overwrite uploaded file'),)

    def __unicode__(self):
        return self.filename

    @property
    def filename(self):
        return os.path.basename(self.content.name)

    @property
    def display_filetype(self):
        for key, value in settings.PYPPI_DIST_FILE_TYPES:
            if key == self.filetype:
                return value
        return self.filetype

    @property
    def path(self):
        return self.content.name

    def get_absolute_url(self):
        return "%s#md5=%s" % (self.content.url, self.md5_digest)


class Review(models.Model):
    release = models.ForeignKey(Release, related_name="reviews")
    rating = models.PositiveSmallIntegerField(blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u'release review')
        verbose_name_plural = _(u'release reviews')


class MirrorSite(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class MirrorLog(models.Model):
    master = models.ForeignKey(MirrorSite, related_name='logs')
    created = models.DateTimeField(default='now')
    releases_added = models.ManyToManyField(Release, blank=True,
                                            related_name='mirror_sources')

    def __unicode__(self):
        return '%s (%s)' % (self.master, str(self.created),)

    class Meta:
        get_latest_by = "created"


class IPRestriction(models.Model):
    user = models.ForeignKey(User, related_name='iprestrictions')
    only_allowed_from = models.IPAddressField(blank=True, null=True)


class KnownHost(models.Model):
    ip = models.IPAddressField(unique=True)
    description = models.CharField(max_length=100)
    user = models.OneToOneField(User, editable=False)
    packages = models.ManyToManyField(Package)

    def save(self, force_insert=False, force_update=False, using=None):
        u, __ = User.objects.get_or_create(username=self.ip)
        self.user = u
        return super(KnownHost, self).save(force_insert, force_update, using)


class Owner(User):
    class Meta:
        proxy = True


class Maintainer(User):
    class Meta:
        proxy = True

