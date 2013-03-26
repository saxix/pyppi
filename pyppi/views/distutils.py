from logging import getLogger

from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.utils.datastructures import MultiValueDict
from django.views.generic import View, ListView

from pyppi.models import Package, Release, Distribution, Classifier
from pyppi.http import get_python_version
from pyppi.storage import FileExistsError, can_upload
from pyppi.util import get_distribution_type
from pyppi.views.base import BasicAuthMixin, CheckPermissionMixin
from pyppi.settings import conf

log = getLogger(__name__)


class RegisterView(BasicAuthMixin, CheckPermissionMixin, View):
    http_method_names = ['post', ]
    permissions = ['pyppi.register_package']

    @transaction.commit_manually
    def post(self, request, *args, **kwargs):
        ret = self._register(request, args, kwargs)
        if ret is None:
            transaction.commit()
            return HttpResponse('release registered')
        transaction.rollback()
        return ret

    def _register(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        user = request.user
        try:
            package = Package.objects.get(name=name)
            log.info('Existing package found for `%s`', package)
        except Package.DoesNotExist:
            log.info('New package created')
            package = Package.objects.create(name=name)
            package.owners.add(request.user)

        if user not in package.owners.all() and user not in package.maintainers.all():
            err = 'You (%s) are not an owner/maintainer of %s' % (user, package.name)
            log.error(err)
            transaction.rollback()
            return HttpResponseForbidden(err)

        version = request.POST.get('version', None).strip()
        metadata_version = request.POST.get('metadata_version', None).strip()

        if not version or not metadata_version:
            log.error('not version or not metadata_version')
            transaction.rollback()
            return HttpResponseBadRequest('Release version and metadata version must be specified')

        if not metadata_version in conf.METADATA_FIELDS:
            transaction.rollback()
            return HttpResponseBadRequest('Metadata version must be one of: %s'
                (', '.join(conf.METADATA_FIELDS.keys()), ))

        self.release, created = Release.objects.get_or_create(package=package,
                                                              version=version)
        if created:
            log.info('Created new release `%s`', self.release)
        else:
            log.info('Existing release found for `%s`', self.release)

        if ('classifiers' in request.POST or 'download_url' in request.POST) and metadata_version == '1.0':
            metadata_version = '1.1'

        self.release.metadata_version = metadata_version

        fields = conf.METADATA_FIELDS[metadata_version]

        if 'classifiers' in request.POST:
            request.POST.setlist('classifier', request.POST.getlist('classifiers'))

        # self.release.package_info = MultiValueDict(dict(filter(lambda t: t[0] in fields,
        #                                                        request.POST.iterlists())))

        self.release.package_info = MultiValueDict(dict([t for t in request.POST.iterlists() if t[0] in fields]))

        for key, value in self.release.package_info.iterlists():
            # self.release.package_info.setlist(key,
            #                                   filter(lambda v: v != 'UNKNOWN', value))
            self.release.package_info.setlist(key, [v for v in value if v != 'UNKNOWN'])

        self.release.save()
        log.info('release `{0}` registered'.format(self.release))
        return None


class UploadView(RegisterView):
    permissions = ['pyppi.upload_package']

    def post(self, request, *args, **kwargs):
        log.info('start uploading')
        ret = self._register(request, *args, **kwargs)
        if ret is None:
            return self._upload(request, *args, **kwargs)
        return ret

    def _upload(self, request, *args, **kwargs):
        log.info('uploading file')
        uploaded = request.FILES.get('content')
        md5_digest = request.POST.get('md5_digest', '')
        try:
            if not can_upload(self.request.user, self.release, uploaded):
                raise FileExistsError()

            distro, isnew = Distribution.objects.get_or_create(release=self.release,
                                                               pyversion=get_python_version(
                                                                   request.POST.get('pyversion', '')),
                                                               filetype=get_distribution_type(
                                                                   request.POST.get('filetype', 'sdist')))
            distro.content = uploaded
            distro.uploader = request.user
            distro.comment = request.POST.get('comment', '')
            distro.signature = request.POST.get('gpg_signature', '')
            distro.md5_digest = md5_digest
            distro.save()
        except FileExistsError as e:
            transaction.rollback()
            err = 'That file has already been uploaded...(%s)' % uploaded.name
            log.error(err)
            return HttpResponseForbidden(err)
        except Exception as e: # NOQA
            transaction.rollback()
            log.exception('Failure when storing upload: %s', e)
            return HttpResponseServerError('Failure when storing upload')

        transaction.commit()
        log.info('File uploaded')
        return HttpResponse('upload accepted')


class ClassifierView(ListView):
    template_name = 'pyppi/classifier.html'
    model = Classifier

    def render_to_response(self, context, **response_kwargs):
        return super(ClassifierView, self).render_to_response(context,
                                                              content_type='text/plain; charset=utf-8',
                                                              **response_kwargs)


# @csrf_exempt
# def index(request):
#     """ Root view of the package index, handle incoming actions from distutils
# or redirect to a more user friendly view """
#     if xmlrpc_views.is_xmlrpc_request(request):
#         return xmlrpc_views.handle_xmlrpc_request(request)
#
#     if distutils_request.is_distutils_request(request):
#         return distutils_request.handle_distutils_request(request)
#
#     return HttpResponseRedirect(reverse('djangopypi2-packages-index'))
#
# def simple_index(request):
#     return list_detail.object_list(
#         request,
#         template_name = 'pypi_frontend/package_list_simple.html',
#         template_object_name = 'package',
#         queryset = Package.objects.all(),
#     )
#
#
# @_mirror_if_not_found('simple')
# def simple_details(request, package_name):
#     try:
#         package = Package.objects.get(name__iexact=package_name)
#     except Package.DoesNotExist:
#         package = get_object_or_404(Package, name__iexact=package_name.replace('_', '-'))
#     # If the package we found is not exactly the same as the name the user typed, redirect
#     # to the proper url:
#     if package.name != package_name:
#         return HttpResponseRedirect(reverse('djangopypi2-simple-package-info', kwargs=dict(package_name=package.name)))
#     return render_to_response('pypi_frontend/package_detail_simple.html',
#                               context_instance=RequestContext(request, dict(package=package)),
#                               mimetype='text/html')
#
# @_mirror_if_not_found('pypi')
# def package_details(request, package_name):
#     package = get_object_or_404(Package, name=package_name)
#     return HttpResponseRedirect(package.get_absolute_url())
#
# @_mirror_if_not_found('pypi')
# def package_doap(request, package_name):
#     package = get_object_or_404(Package, name=package_name)
#     return render_to_response('pypi_frontend/package_doap.xml',
#                               context_instance=RequestContext(request, dict(package=package)),
#                               mimetype='text/xml')
#
# def release_doap(request, package_name, version):
#     release = get_object_or_404(Release, package__name=package_name, version=version)
#     return render_to_response('pypi_frontend/release_doap.xml',
#                               context_instance=RequestContext(request, dict(release=release)),
#                               mimetype='text/xml')
#
# @basic_auth
# @transaction.commit_manually
# def register_or_upload(request):
#     if request.method != 'POST':
#         transaction.rollback()
#         return HttpResponseBadRequest('Only post requests are supported')
#
#     name = request.POST.get('name',None).strip()
#
#     if not name:
#         transaction.rollback()
#         return HttpResponseBadRequest('No package name specified')
#
#     try:
#         package = Package.objects.get(name=name)
#     except Package.DoesNotExist:
#         package = Package.objects.create(name=name)
#         package.owners.add(request.user)
#
#     if (request.user not in package.owners.all() and
#         request.user not in package.maintainers.all()):
#
#         transaction.rollback()
#         return HttpResponseForbidden('You are not an owner/maintainer of %s' % (package.name,))
#
#     version = request.POST.get('version',None).strip()
#     metadata_version = request.POST.get('metadata_version', None).strip()
#
#     if not version or not metadata_version:
#         transaction.rollback()
#         return HttpResponseBadRequest('Release version and metadata version must be specified')
#
#     if not metadata_version in settings.DJANGOPYPI_METADATA_FIELDS:
#         transaction.rollback()
#         return HttpResponseBadRequest('Metadata version must be one of: %s'
#                                       (', '.join(settings.DJANGOPYPI_METADATA_FIELDS.keys()),))
#
#     release, created = Release.objects.get_or_create(package=package,
#                                                      version=version)
#
#     if (('classifiers' in request.POST or 'download_url' in request.POST) and
#         metadata_version == '1.0'):
#         metadata_version = '1.1'
#
#     release.metadata_version = metadata_version
#
#     fields = settings.DJANGOPYPI_METADATA_FIELDS[metadata_version]
#
#     if 'classifiers' in request.POST:
#         request.POST.setlist('classifier',request.POST.getlist('classifiers'))
#
#     release.package_info = MultiValueDict(dict(filter(lambda t: t[0] in fields,
#                                                       request.POST.iterlists())))
#
#     for key, value in release.package_info.iterlists():
#         release.package_info.setlist(key,
#                                      filter(lambda v: v != 'UNKNOWN', value))
#
#     release.save()
#     if not 'content' in request.FILES:
#         transaction.commit()
#         return HttpResponse('release registered')
#
#     uploaded = request.FILES.get('content')
#
#     for dist in release.distributions.all():
#         if os.path.basename(dist.content.name) == uploaded.name:
#             """ Need to add handling optionally deleting old and putting up new """
#             transaction.rollback()
#             return HttpResponseBadRequest('That file has already been uploaded...')
#
#     md5_digest = request.POST.get('md5_digest','')
#
#     try:
#         new_file = Distribution.objects.create(release=release,
#                                                content=uploaded,
#                                                filetype=request.POST.get('filetype','sdist'),
#                                                pyversion=request.POST.get('pyversion',''),
#                                                uploader=request.user,
#                                                comment=request.POST.get('comment',''),
#                                                signature=request.POST.get('gpg_signature',''),
#                                                md5_digest=md5_digest)
#     except Exception, e:
#         transaction.rollback()
#         log.exception('Failure when storing upload')
#         return HttpResponseServerError('Failure when storing upload')
#
#     transaction.commit()
#
#     return HttpResponse('upload accepted')
#
# def list_classifiers(request, mimetype='text/plain'):
#     response = HttpResponse(mimetype=mimetype)
#     response.write(u'\n'.join(map(lambda c: c.name,Classifier.objects.all())))
#     return response
