# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from math import floor, log
import os.path

# Using django six if present
try:
    from django.utils import six
except ImportError:
    import six

BytesIO = six.BytesIO


class MiniatureParserError(Exception):
    pass


class BaseProcessor(object):
    FILTERS = {}
    DEFAULT_FILTER = None

    MODES = {}

    def __init__(self, img):
        if isinstance(img, six.string_types):
            self.fp = open(img, 'rb')
        elif hasattr(img, 'read'):
            self.fp = img
        else:
            raise TypeError('Processor first argument should be a path or a file descriptor.')

        self.img, self.info = self._open_image(self.fp)
        self.info['format'] = self.info['format'].lower()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def __del__(self):
        self.close()

    @property
    def format(self):
        return self.info['format']

    @property
    def size(self):
        self.assert_open()
        return self._get_size(self.img)

    @property
    def mode(self):
        self.assert_open()
        return self._get_mode(self.img)

    def save(self, file, format=None, **options):
        self.assert_open()

        filename = None
        if isinstance(file, six.string_types):
            filename = file
        else:
            if not hasattr(file, 'write'):
                raise TypeError('file argument should be a string or a file descriptor.')
            options['file'] = file

        format_ = format
        if filename is not None:
            base, ext = os.path.splitext(filename)
            ext = ext[1:]

            # Get format from extension
            if format_ is None:
                format_ = ext.lower()
                if format_ == 'jpg':
                    format_ = 'jpeg'
            else:
                format_ = format_.lower()

            if not format_:
                format_ = self.format

            # Check if format match extension
            if not (format_ == ext or format_ == 'jpeg' and ext.lower() == 'jpg'):
                base = filename
                ext = format_

            options['filename'] = '{0}.{1}'.format(base, ext)

        if format_ == 'jpeg':
            options.setdefault('quality', 85)

        self._raw_save(self.img, format_ or self.format, **options)
        return self

    def close(self):
        if getattr(self, 'img', None) is not None:
            self._close(self.img)
            del(self.img)

        if getattr(self, 'fp', None) is not None:
            self.fp.close()

    def color(self, color):
        if isinstance(color, six.string_types) and color.startswith('#'):
            color = color[1:]
            if len(color) in (3, 4):
                color = '#{0}'.format(''.join([x * 2 for x in color]))

        return self._get_color(color)

    def set_mode(self, mode, **options):
        self.assert_open()
        self.img = self._set_mode(self.img, mode, **options)
        return self

    def set_background(self, color):
        self.assert_open()
        self.img = self._set_background(self.img, self.color(color))
        return self

    def crop(self, *args):
        self.assert_open()

        def percent_to_px(value, base):
            if isinstance(value, six.string_types):
                value = floor(float(value.rstrip('%')) / 100 * base)

            return int(value)

        aliases = {
            'center': [0, 0],
            'top-left': ['-100%', '-100%'],
            'top-right': ['100%', '-100%'],
            'bottom-left': ['-100%', '100%'],
            'bottom-right': ['100%', '100%'],
        }
        args = list(args)

        w, h = self.size
        center = (int(floor(w / 2)), int(floor(h / 2)))
        offset_x = offset_y = None

        if len(args) == 2 and args[1] in aliases:
            # Aliases
            args = args[0:1] + aliases[args[1]]

        if len(args) == 2 and args[1] == 'smart':
            # Smart crop, move the center to POI
            poi = self.get_poi()
            args = args[0:1] + [poi[0] - center[0], poi[1] - center[1]]

        if len(args) == 4:
            # Basic crop with coordinates
            x1, y1, x2, y2 = args
            if x2 <= 0:
                x2 = w + x2
            if y2 <= 0:
                y2 = h + y2
        elif len(args) == 3:
            # Position + ratio crop
            ratio, offset_x, offset_y = args
            nw, nh = w, h
            if ratio > w / h:
                nh = int(floor(w / ratio))
            else:
                nw = int(floor(h * ratio))

            offset_x = percent_to_px(offset_x, w / 2)
            offset_y = percent_to_px(offset_y, h / 2)

            # Get starting points
            x1 = center[0] - int(floor(nw / 2))
            y1 = center[1] - int(floor(nh / 2))
            x2 = x1 + nw
            y2 = y1 + nh

            # Move center inside image boundaries
            if offset_x > 0:
                x2 = min(w, x2 + offset_x)
                x1 = x2 - nw

            if offset_x < 0:
                x1 = max(0, x1 + offset_x)
                x2 = x1 + nh

            if offset_y > 0:
                y2 = min(h, y2 + offset_y)
                y1 = y2 - nh

            if offset_y < 0:
                y1 = max(0, y1 + offset_y)
                y2 = y1 + nh
        else:
            raise ValueError('Invalid crop options "{0}".'.format(args))

        self.img = self._crop(self.img, x1, y1, x2, y2)
        return self

    def resize(self, w, h, filter=None):
        self.assert_open()
        self.img = self._resize(self.img, w, h, self.FILTERS.get(filter) or self.DEFAULT_FILTER)
        return self

    def thumbnail(self, w, h, filter=None, upscale=False):
        self.assert_open()

        self.img = self._thumbnail(self.img, w, h,
            self.FILTERS.get(filter) or self.DEFAULT_FILTER,
            upscale
        )
        return self

    def rotate(self, angle):
        self.assert_open()
        self.img = self._rotate(self.img, angle)
        return self

    def add_border(self, width, color):
        self.assert_open()
        self.img = self._add_border(self.img, width, self.color(color))
        return self

    #
    # Utils
    #
    def assert_open(self):
        if not hasattr(self, 'img'):
            raise AttributeError('Processor is closed.')

    def get_histogram(self):
        self.assert_open()
        return self._get_histogram(self.img)

    def get_poi(self, size=210, block_size=70):
        """
        Returns the image zone coordinates with most information (point of interest)
        """
        self.assert_open()
        if size % block_size != 0:
            raise ValueError('block_size should be a multiple of size.')

        img = self._copy_image(self.img)
        img = self._thumbnail(img, size, size, self.DEFAULT_FILTER, False)
        # img = self._set_mode(img, 'grayscale')

        w, h = self._get_size(img)
        cols = min(size // block_size, w // block_size)
        rows = min(size // block_size, h // block_size)
        zones = []

        for x in range(0, cols):
            for y in range(0, rows):
                tmp_ = self._copy_image(img)
                x1 = x * block_size
                y1 = y * block_size
                x2 = x1 + block_size <= w and x1 + block_size or w
                y2 = y1 + block_size <= h and y1 + block_size or h
                coords = (x1, y1, x2, y2)

                tmp_ = self._crop(tmp_, *coords)
                zones.append((coords, self._get_entropy(tmp_)))
                tmp_.close()

        self._close(img)
        zones.sort(key=lambda x: x[1], reverse=True)

        w, h = self._get_size(self.img)
        ratio = max(w, h) / size
        zone = tuple(int(x * ratio) for x in zones[0][0])
        return (
            (zone[2] - zone[0]) // 2 + zone[0],
            (zone[3] - zone[1]) // 2 + zone[1],
        )

    def _get_color(self, color):
        """
        Default color parser
        """
        if isinstance(color, six.string_types):
            # Hex color definition
            color = color.lstrip('#')
            if len(color) not in (6, 8):
                raise TypeError('Invalid color definition "{0}".'.format(color))

            return tuple(int(color[i:(i + 2)], 16) for i in range(0, len(color), 2))
        elif isinstance(color, (list, tuple)):
            return color
        else:
            raise TypeError('Invalid color definition "{0}".'.format(color))

    def _get_entropy(self, img):
        histogram = self._get_histogram(img)
        size = sum(histogram)
        histogram = [x / size for x in histogram]
        return -sum(tuple(p * log(p, 2) for p in histogram if p != 0))

    #
    # Methods to implement
    #
    def _open_image(self, fp):
        raise NotImplementedError

    def _raw_save(self, img, format, **options):
        raise NotImplementedError

    def _close(self, img):
        raise NotImplementedError

    def _copy_image(self, img):
        raise NotImplementedError

    def _get_size(self, img):
        raise NotImplementedError

    def _get_mode(self, img):
        raise NotImplementedError

    def _set_mode(self, img, mode, **options):
        raise NotImplementedError

    def _set_background(self, img, color):
        raise NotImplementedError

    def _crop(self, img, x1, y1, x2, y2):
        raise NotImplementedError

    def _resize(self, img, w, h, filter):
        raise NotImplementedError

    def _thumbnail(self, img, w, h, filter, upscale):
        raise NotImplementedError

    def _rotate(self, img, angle):
        raise NotImplementedError

    def _add_border(self, img, width, color):
        raise NotImplementedError

    def _get_histogram(self, img):
        raise NotImplementedError
