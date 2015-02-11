# -*- coding: utf-8 -*-
#
# This file is part of Django facets released under the MIT license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from django import forms
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from miniature.thumbnails import get_thumbnail


class ImageWidget(forms.ClearableFileInput):
    template_with_initial = '%(clear_template)s %(input_text)s: %(input)s'
    template_with_clear = \
        '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label><br />'

    template_with_img = '<img src="{src}" alt="{initial}" /> <br /> ' \
        '{original_txt}: <a href="{url}">{url}</a> <br /> {widget}'
    operations = (('thumbnail', '300,'),)

    def __init__(self, *args, **kwargs):
        self.operations = kwargs.pop('operations', self.operations)
        self.html_tpl = kwargs.pop('html_tpl',
            '<img src="{src}" alt="" /> <br />{widget}'
        )
        super(ImageWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = super(ImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                mini = get_thumbnail(value, self.operations)
            except:
                raise
            else:
                output = format_html(self.template_with_img,
                    src=mini.url, initial=force_text(value), widget=output,
                    original_txt='Original', url=value.url
                )
        return mark_safe(output)


class ImageFormField(forms.ImageField):
    widget = ImageWidget
