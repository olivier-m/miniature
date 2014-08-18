# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

from PIL import Image, ImageColor

from .base import BaseProcessor


class Processor(BaseProcessor):
    FILTERS = {
        'antialias': Image.ANTIALIAS,
        'nearest': Image.NEAREST,
        'bilinear': Image.BILINEAR,
        'bicubic': Image.BICUBIC,
    }
    DEFAULT_FILTER = Image.ANTIALIAS

    MODES = {
        'bilevel': '1',
        'grayscale': 'L',
        'grayscalematte': 'LA',
        'palette': 'P',
        'palettematte': 'PA',
        'truecolor': 'RGB',
        'truecolormatte': 'RGBA',
        'colorseparation': 'CMYK',
    }

    def _open_image(self, fp):
        im = Image.open(fp)
        info = im.info
        info.update({
            'format': im.format
        })
        return im, info

    def _close(self, img):
        img.close()

    def _raw_save(self, img, format, **options):
        fp = options.pop('file', None) or options.pop('filename')
        img.save(fp=fp, format=format.upper(), **options)

    def _copy_image(self, img):
        return img.copy()

    def _get_color(self, color):
        try:
            return super(Processor, self)._get_color(color)
        except TypeError:
            return ImageColor.getrgb(color)

    def _get_size(self, img):
        return img.size

    def _get_mode(self, img):
        return dict((v, k) for k, v in self.MODES.items())[img.mode]

    def _set_mode(self, img, mode, **options):
        options.setdefault('palette', Image.ADAPTIVE)

        mode = self.MODES[mode]
        return img.convert(mode, **options)

    def _orientation(self, img):
        try:
            exif = img._getexif()
        except (AttributeError, IOError, KeyError, IndexError):
            return img

        if exif is None:
            return img

        orientation = exif.get(0x0112)

        if orientation == 2:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            img = img.rotate(180)
        elif orientation == 4:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            img = img.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            img = img.rotate(-90)
        elif orientation == 7:
            img = img.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            img = img.rotate(90)

        return img

    def _set_background(self, img, color):
        bg = Image.new('RGBA', self.img.size, color)
        bg.paste(self.img, mask=self.img)
        return bg

    def _crop(self, img, x1, y1, x2, y2):
        return img.crop((x1, y1, x2, y2))

    def _resize(self, img, w, h, filter=None):
        return img.resize((w, h), filter)

    def _rotate(self, img, angle):
        return img.rotate(-angle, resample=Image.BICUBIC, expand=True)

    def _add_border(self, img, width, color):
        bg = Image.new('RGBA', [sum(x) for x in zip(img.size, [width * 2] * 2)], color)
        bg.paste(img, (width,) * 2)
        return bg

    def _get_histogram(self, img):
        return img.histogram()
