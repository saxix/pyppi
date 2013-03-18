# -*- coding: utf-8 -*-
from inspect import ismethod
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext as _
from django.db.models import Model
from django import template


register = template.Library()

DJANGO_BREADCRUMB_CONTEXT_KEY = 'DJANGO_BREADCRUMBS_LIST'


class BreadcrumbNode(template.Node):
    def __init__(self, label, viewname, *args, **kwargs):
        self.label = template.Variable(label)
        self.viewname = template.Variable(viewname)
        self.context_var = kwargs.pop('context_var', DJANGO_BREADCRUMB_CONTEXT_KEY)
        self.args = [template.Variable(a) for a in args]
        self.kwargs = kwargs

    def render(self, context):
        label = self.label.resolve(context)
        viewname = self.viewname.resolve(context)
        args = [a.resolve(context) for a in self.args]
        context['request'].META[self.context_var] = context['request'].META.get(self.context_var, []) + [
            (label, viewname, args)]
        return ''


@register.tag
def breadcrumb(parser, token):
    """

    Examples:
    {% breadcrumb "Home" "index" %}
    {% breadcrumb "Employees" "views.employees.list" office.code %}
    {% render_breadcrumbs %}


    {% breadcrumb "Home" "index" as 'B2' %}
    {% breadcrumb "Employees" "views.employees.list" office.code  as 'B2' %}
    {% render_breadcrumbs 'B2' %}


    :param parser:
    :param token:
    :return:
    """
    bits = token.split_contents()
    format = '{% breadcrumb label viewname *viewargs [as "context_var"] %}'
    if len(bits) < 3 or ('as' in bits and len < bits.index('as') + 1):
        raise template.TemplateSyntaxError("get_office_perm tag should be in format: %s" % format)

    label = bits[1]
    viewname = bits[2]
    if 'as' in bits:
        context_var = bits[bits.index('as') + 1]
        if context_var[0] != context_var[-1] or context_var[0] not in ('"', "'"):
            raise template.TemplateSyntaxError("breadcrumb tag's context_var argument should be in quotes")

        context_var = bits[bits.index('as') + 1][1:-1]
        args = bits[3:-2]
    else:
        args = bits[3:]
        context_var = DJANGO_BREADCRUMB_CONTEXT_KEY

    return BreadcrumbNode(label, viewname, context_var=context_var, *args)


@register.inclusion_tag('breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context, context_var=DJANGO_BREADCRUMB_CONTEXT_KEY):
    links = []
    for (label, viewname, args) in context['request'].META.get(context_var, []):
        if isinstance(viewname, Model) and hasattr(
                viewname, 'get_absolute_url') and ismethod(
                viewname.get_absolute_url):
            url = viewname.get_absolute_url()
        else:
            try:
                url = reverse(viewname=viewname, args=args)
            except NoReverseMatch:
                url = viewname
        links.append((url, _(unicode(label)) if label else label))

    if not links:
        return ''
    return {'breadcrumbs': links}

