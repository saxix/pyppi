"""Default variable filters."""
import logging
import os
from django.template.base import Library
from django.template.defaultfilters import filesizeformat
from pyppi.util import user_can_download

register = Library()
logger = logging.getLogger(__name__)


@register.filter(is_safe=True)
def filesize(fieldfile):
    if os.path.isfile(fieldfile.name):
        return filesizeformat(fieldfile.size)


@register.filter(is_safe=True)
def isfile(fieldfile):
    return os.path.isfile(fieldfile.name)


@register.assignment_tag(takes_context=True)
def can_download(context, distro):
    request = context['request']
    has_perm = user_can_download(request, distro)
    logger.debug('Check if {request.user} can download {distro.release.package}: {has_perm}'.format(**locals()))
    return has_perm
