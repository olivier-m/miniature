# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from django.utils.functional import LazyObject
from django.utils.module_loading import import_by_path

from miniature.thumbnails.conf import settings


class Backend(LazyObject):
    def _setup(self):
        self._wrapped = import_by_path(settings.MINIATURE_BACKEND)

backend = Backend()


def get_thumbnail(image, operations=None, timeout=None):
    return backend.get_thumbnail(image, operations, timeout)
