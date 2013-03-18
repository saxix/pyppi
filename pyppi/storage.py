import os
import re
from logging import getLogger
from django.core.files.storage import FileSystemStorage
from pyppi.settings import conf

log = getLogger(__name__)


class FileExistsError(Exception):
    pass


def can_upload(user, release, uploaded):
    version = release.version
    can_override = False

    if user.has_perm('pyppi.overwrite_file'):
        allowed = conf.ALLOW_VERSION_OVERWRITE
        if allowed:
            can_override = re.search(allowed, version)

    for dist in release.distributions.all():
        if os.path.basename(dist.content.name) == uploaded.name:
            return can_override

    return True


class PyppiStorage(FileSystemStorage):
    """
    Returns same name for existing file and deletes existing file on save.
    """

    def _save(self, name, content):

        if self.exists(name):
            if conf.ALLOW_VERSION_OVERWRITE:
                log.warning("File `%s` exists but user allowed to overwrite", name)
                os.unlink(self.path(name))
            else:
                raise FileExistsError(os.path.abspath(name))
        return super(PyppiStorage, self)._save(name, content)

    def get_available_name(self, name):
        return name
