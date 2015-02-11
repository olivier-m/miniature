# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import hashlib
import os.path

from django.core.cache import get_cache, cache as default_cache, InvalidCacheBackendError
from django.core.files.base import File, ContentFile
from django.core.files.storage import get_storage_class, default_storage
from django.utils.encoding import force_bytes, force_text
from django.utils.functional import LazyObject
from django.utils import six
from django.utils.six.moves.urllib.parse import urljoin, urlsplit
from django.utils.six.moves.urllib.request import urlopen

from miniature.processor import get_processor
from miniature.thumbnails.conf import settings


class ThumbnailCache(LazyObject):
    def _setup(self):
        try:
            self._wrapped = get_cache(settings.MINIATURE_CACHE)
        except InvalidCacheBackendError:
            self._wrapped = default_cache


class ThumbnailStorage(LazyObject):
    def _setup(self):
        prefix = settings.MINIATURE_THUMBNAIL_PATH
        if prefix.endswith('/'):
            prefix = prefix[0:-1]

        base_path = os.path.join(settings.MEDIA_ROOT, prefix)
        base_url = urljoin(settings.MEDIA_URL, '{0}/'.format(prefix))
        self._wrapped = get_storage_class()(location=base_path, base_url=base_url)


class ThumbnailBackend(object):
    Processor = get_processor(settings.MINIATURE_PROCESSOR)
    storage = ThumbnailStorage()
    cache = ThumbnailCache()

    @classmethod
    def image_id(cls, image):
        return force_bytes(image.path)

    @classmethod
    def op_id(cls, operations):
        return hashlib.md5(force_bytes(repr(operations))).hexdigest()

    @classmethod
    def get_entries(cls, image):
        return cls.cache.get(cls.image_id(image))

    @classmethod
    def set_entries(cls, image, entries, timeout=None):
        cls.cache.set(cls.image_id(image), entries, timeout)

    @classmethod
    def remove_entries(cls, image, remove_files=False):
        entries = cls.get_entries(image)
        if entries:
            for name in entries.values():
                cls.storage.delete(name)

        cls.cache.delete(cls.image_id(image))

    @classmethod
    def get_thumbnail(cls, image, operations=None, timeout=None):
        operations = operations or []

        url = None
        if isinstance(image, six.string_types):
            if urlsplit(image).scheme in ('http', 'https'):
                url = image
                image = six.BytesIO()
                image.path = url

        op_id = cls.op_id(operations)
        entries = cls.get_entries(image)
        if entries is None:
            entries = {}

        cached_path = entries.get(op_id)
        if cached_path is not None and not cls.storage.exists(cached_path):
            # Something in cache but no file, drop entry
            del entries[op_id]
            cached_path = None

        if not cached_path:
            img_id = hashlib.md5(force_bytes('{0}{1}'.format(
                image.path,
                repr(operations)))
            ).hexdigest()

            # Open URL if needed
            if url:
                rsp = None
                try:
                    rsp = urlopen(url)
                    image.write(rsp.read())
                    image.seek(0)
                finally:
                    if rsp:
                        rsp.close()

            # Create thumbnail
            dest_file = ContentFile('')

            if hasattr(image, 'closed') and image.closed:
                image.open()

            with cls.Processor(image) as p:
                p.orientation()
                p.operations(*operations).save(dest_file)

                cached_path = '{0}.{1}'.format(
                    os.path.join(img_id[0:2], img_id[2:4], img_id),
                    p.format
                )
                cls.storage.save(cached_path, dest_file)
                del dest_file

            if hasattr(image, 'close'):
                image.close()

        entries[op_id] = cached_path
        cls.set_entries(image, entries, timeout)
        return FileWrapper(cached_path, cls.storage)


class FileWrapper(File):
    """
    This is the miniature file wrapper returned by template tag and used in the following storage
    class
    """
    def __init__(self, file_, storage=None):
        name = getattr(file_, 'name', None)
        if not name:
            name = force_text(file_)

        super(FileWrapper, self).__init__(None, name)

        if storage is not None:
            self.storage = storage
        elif hasattr(file_, 'storage'):
            self.storage = file_.storage
        else:
            self.storage = default_storage

    @property
    def url(self):
        return self.storage.url(self.name)

    @property
    def path(self):
        return self.storage.path(self.name)
