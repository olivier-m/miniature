# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from django import template
from django.template.base import kwarg_re

from miniature.thumbnails.conf import settings
from miniature.thumbnails import get_thumbnail

register = template.Library()


class ThumbnailNode(template.Node):
    def __init__(self, nodelist, tag_name, file_instance, var_name, params):
        self.nodelist = nodelist
        self.tag_name = tag_name
        self.var_name = var_name
        self.file_instance = file_instance
        self.params = params
        self.presets = settings.MINIATURE_PRESETS

    def __repr__(self):
        return "<ThumbnailNode>"

    def render(self, context):
        operations = self.get_operations(context)
        img = get_thumbnail(self.file_instance.resolve(context), operations)
        context.update({self.var_name: img})
        output = self.nodelist.render(context)
        context.pop()
        return output

    def get_operations(self, context):
        result = []
        for name, value in self.params:
            value = value.resolve(context)
            if name is None:
                try:
                    value = self.presets[value]
                    result.extend(value)
                except KeyError:
                    raise template.TemplateSyntaxError('Preset "{0}" does not exist.'.format(value))
            else:
                result.append((name, value))

        return result


@register.tag('thumbnail')
def do_thumbnail(parser, token):
    bits = token.split_contents()
    tag_name = bits.pop(0)

    try:
        if bits.pop(-2) != 'as':
            raise ValueError()
        var_name = bits.pop()
        file_instance = parser.compile_filter(bits.pop(0))
    except ValueError:
        raise template.TemplateSyntaxError(
            '{0} tag syntax is "file [params] as varname".'.format(tag_name)
        )

    params = []
    while bits:
        match = kwarg_re.match(bits.pop(0))
        if match and match.group(1):
            k, v = match.groups()
            params.append((k, parser.compile_filter(v)))
        else:
            params.append((None, parser.compile_filter(match.group(2))))

    nodelist = parser.parse(('endthumbnail',))
    parser.delete_first_token()
    return ThumbnailNode(nodelist, tag_name, file_instance, var_name, params)
