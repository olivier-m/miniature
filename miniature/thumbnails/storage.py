# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import os.path

from django.core.files.storage import get_storage_class

from miniature.thumbnails import backend
from miniature.thumbnails.base import FileWrapper

DefaultStorage = get_storage_class()


class MiniatureStorageMixin(object):
    """
    A storage you can use for FileField model fields.
    It removes thumbnails when the file is removed.
    """
    image_extensions = ('bmp', 'jpg', 'jpeg', 'gif', 'png', 'svg', 'tiff')

    def _clear_thumbnails(self, name):
        file_ = FileWrapper(name, storage=self)
        backend.remove_entries(file_, remove_files=True)

    def delete(self, name):
        super(MiniatureStorageMixin, self).delete(name)
        self._clear_thumbnails(name)

    def is_image(self, name):
        return os.path.splitext(name)[1][1:].lower() in self.image_extensions


class MiniatureStorage(MiniatureStorageMixin, DefaultStorage):
    pass
