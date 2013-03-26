from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.core.urlresolvers import reverse
from pyppi.models import Review, Package, Release, Distribution, Classifier, Maintainer, Owner, \
    PlatformName, PythonVersion, Architecture, DistributionType, MirrorSite, MirrorLog, IPRestriction, KnownHost


class ClassifierAdmin(ModelAdmin):
    search_fields = ('name',)


class ReviewInline(TabularInline):
    model = Review
    list_display = ('rating', )


class PackageInline(TabularInline):
    model = Package
    extra = 0


class ReleaseInline(TabularInline):
    model = Release
    extra = 0
    list_display = ('version', 'platform', 'metadata_version', 'hidden', 'created')

    def platform(self, obj):
        return obj.package_info.get('platform', u'')


class DistributionInline(TabularInline):
    model = Distribution
    list_display = ('content', 'display_filetype', 'pyversion', 'created', 'uploader')
    readonly_fields = ('content', 'filetype', 'pyversion', 'created', 'uploader', 'comment', 'signature')
    extra = 0


class PackageAdmin(ModelAdmin):
    list_display = ('name', 'latest', 'auto_hide', 'allow_comments', '_owners')
    list_filter = ('auto_hide', 'allow_comments', )
    search_fields = ('name',)
    inlines = [ReleaseInline]
    filter_horizontal = ('owners', 'maintainers', 'classifiers')

    def _owners(self, obj):
        return ",".join(obj.owners.values_list('username', flat=True))

    def latest(self, obj):
        url = reverse("admin:pyppi_release_change", args=[obj.latest.pk])
        return '<a href="{1}">{0.latest}</a>'.format(obj, url)

    latest.allow_tags = True


class ReleaseAdmin(ModelAdmin):
    list_display = ('release_name', 'package_ref', 'version', 'created', 'visible')
    list_filter = ('package', 'created', 'hidden', )
    date_hierarchy = 'created'
    search_fields = ('package__name',)
    inlines = [DistributionInline, ReviewInline]

    def visible(self, obj):
        return not obj.hidden

    visible.boolean = True

    def package_ref(self, obj):
        url = reverse("admin:pyppi_package_change", args=[obj.package.pk])
        return '<a href="{1}">{0.package.pk}</a>'.format(obj, url)

    package_ref.admin_order_field = 'package__name'
    package_ref.allow_tags = True
    package_ref.short_description = 'package'


class DistributionAdmin(ModelAdmin):
    list_display = ('name', 'package', 'version', 'release_ref', 'pyversion', 'created', 'uploader')
    list_filter = ('filetype', 'platform')
    search_fields = ('release__package__name', 'content')
    date_hierarchy = 'created'

    def name(self, obj):
        return "{0.release.package} {0.release.version}".format(obj)

    def package(self, obj):
        url = reverse("admin:pyppi_package_change", args=[obj.release.package.pk])
        return '<a href="{1.release.package}">{0}</a>'.format(obj, url)

    package.admin_order_field = 'package__name'

    def version(self, obj):
        return obj.release.version

    version.admin_order_field = 'release__version'

    def release_ref(self, obj):
        url = reverse("admin:pyppi_release_change", args=[obj.release.pk])
        return '<a href="{1}">{0.release.release_name}</a>'.format(obj, url)

    release_ref.short_description = 'release'
    release_ref.allow_tags = True


class KnownHostAdmin(ModelAdmin):
    search_fields = ('description', )
    list_display = ('ip', 'description')
    filter_horizontal = ('packages',)


class IPRestrictionAdmin(ModelAdmin):
    search_fields = ('user', )
    list_filter = ('user', )
    list_display = ('user', 'only_allowed_from')


class MaintainerAdmin(UserAdmin):
    pass


class OwnerAdmin(UserAdmin):
    pass


def register(model, modeladmin=None):
    try:
        admin.site.unregister(model)
    except NotRegistered:
        pass
    admin.site.register(model, modeladmin)


def override():
    register(Classifier, ClassifierAdmin)
    register(Distribution, DistributionAdmin)
    register(Package, PackageAdmin)
    register(Release, ReleaseAdmin)
    register(Maintainer, MaintainerAdmin)
    register(Owner, OwnerAdmin)
    register(PlatformName)
    register(PythonVersion)
    register(Architecture)
    register(DistributionType)
    register(Review)
    register(MirrorSite)
    register(MirrorLog)
    register(IPRestriction, IPRestrictionAdmin)
    register(KnownHost, KnownHostAdmin)
