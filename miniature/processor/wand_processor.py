# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from wand.api import library
from wand.image import Image, HistogramDict
from wand.color import Color

from .base import BaseProcessor


def fast_histogram(img):
    h = HistogramDict(img)
    pixels = h.pixels
    return tuple(
        library.PixelGetColorCount(pixels[i])
        for i in range(h.size.value)
    )


class Processor(BaseProcessor):
    def _open_image(self, fp):
        im = Image(file=fp)
        info = {}
        for k, v in im.metadata.items():
            if ':' not in k:
                continue
            ns, k = k.split(':')
            if ns not in info:
                info[ns] = {}
            info[ns][k] = v

        info.update({
            'format': im.format
        })

        return im, info

    def _close(self, img):
        img.destroy()

    def _raw_save(self, img, format, **options):
        img.format = format
        if img.format == 'JPEG':
            img.compression_quality = options.pop('quality', 85)

        img.save(**options)

    def _copy_image(self, img):
        return img.clone()

    def _get_color(self, color):
        return Color(color)

    def _get_size(self, img):
        return img.size

    def _get_mode(self, img):
        return img.type

    def _set_mode(self, img, mode, **options):
        img.type = mode
        return img

    def _set_background(self, img, color):
        bg = Image().blank(img.width, img.height, background=color)
        bg.type = img.type
        bg.composite(img, 0, 0)
        img.destroy()
        return bg

    def _crop(self, img, x1, y1, x2, y2):
        img.crop(x1, y1, x2, y2)
        return img

    def _resize(self, img, w, h, filter):
        img.resize(w, h, filter or 'undefined')
        return img

    def _thumbnail(self, img, w, h, filter, upscale):
        geometry = upscale and '{0}x{1}' or '{0}x{1}>'
        img.transform(resize=geometry.format(w, h))
        return img

    def _rotate(self, img, angle):
        img.rotate(angle)
        return img

    def _add_border(self, img, width, color):
        bg = Image().blank(img.width + width * 2, img.height + width * 2, color)
        bg.composite(img, width, width)
        img.destroy()
        return bg

    def _get_histogram(self, img):
        return fast_histogram(img)
