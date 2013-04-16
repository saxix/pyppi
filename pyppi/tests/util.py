import operator
from contextlib import contextmanager
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from pyppi.models import IPRestriction
from guardian.models import UserObjectPermission


def perms(*names):
    filters = []
    for name in names:
        if '.' in name:
            app_label, codename = name.split('.')
            filters.append(Q(content_type__app_label=app_label, codename=codename))
        else:
            filters.append(Q(content_type__app_label=name))
    return Permission.objects.filter(reduce(operator.or_, filters))


@contextmanager
def user_add_permission(user, permission_names, obj=None, limit_from=None):
    """
        temporary add permissions to user

    :param user:
    :param permissions: list
    :return:

    >>> u = User()
    >>> o = Group()
    >>> u.has_perm('test', o)
    False
    >>> with user_add_permission(u, o, ['test']):
    ...     u.has_perm('test', o)
    True
    >>> u.has_perm('test', o)
    False
    """
    assert isinstance(permission_names, (list, tuple)), '`permission_names` must be a list of strings'
    try:
        created = []
        permissions = perms(*permission_names)
        if obj:
            for perm in permissions:
                p, __ = UserObjectPermission.objects.get_or_create(permission=perm,
                                                                   content_type=ContentType.objects.get_for_model(obj),
                                                                   user=user,
                                                                   object_pk=obj.pk)
                created.append(p)
        else:
            for perm in permissions:
                user.user_permissions.add(perm)
        if limit_from:
            ipr, __ = IPRestriction.objects.get_or_create(user=user, only_allowed_from=limit_from)
            ipr.save()
        yield
    finally:
        if obj:
            for p in created:
                p.delete()
        else:
            for p in permissions:
                user.user_permissions.remove(p)
        if limit_from:
            ipr.delete()


# @contextmanager
# def clean_dist_dir(func=None):
#     old_content = None
#     try:
#         dest = os.path.join(settings.MEDIA_ROOT, Distribution._meta.get_field('content').upload_to)
#         old_content = os.listdir(dest)
#         yield
#     except:
#         raise
#     finally:
#         if old_content:
#             for f in os.listdir(dest):
#                 if f not in old_content:
#                     os.unlink(os.path.join(dest, f))
#
