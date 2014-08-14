# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from miniature.processor.base import six
from miniature.processor import get_processor

DEST_FOLDER = None
if 'DEST_FOLDER' in os.environ:
    DEST_FOLDER = os.path.realpath(os.environ['DEST_FOLDER'])


class ProcessorTestCase(object):
    processor = None
    assets = os.path.realpath(os.path.join(os.path.dirname(__file__), 'assets'))
    tmp_folder = DEST_FOLDER

    def setUp(self):
        if not self.tmp_folder:
            self.dest = mkdtemp()
        else:
            self.dest = self.tmp_folder

    def tearDown(self):
        if not self.tmp_folder:
            rmtree(self.dest)

    def get_asset(self, name):
        return os.path.join(self.assets, name)

    def get_dest(self, name):
        name = '{0}-{1}'.format(self.processor.__module__.split('.')[-1], name)
        return os.path.join(self.dest, name)

    def test_open_file(self):
        with self.processor(self.get_asset('tiger.jpg')) as img:
            img.save(self.get_dest('tiger-1.jpg'))

    def test_open_buffer(self):
        with open(self.get_asset('tiger.jpg'), 'rb') as fp:
            with self.processor(fp) as img:
                img.save(self.get_dest('tiger-2.jpg'))

    def test_open_buffer2(self):
        with open(self.get_asset('tiger.jpg'), 'rb') as fp:
            b = six.BytesIO(fp.read())

        with self.processor(b) as img:
            img.save(self.get_dest('tiger-3.jpg'))

    def test_save_buffer(self):
        with self.processor(self.get_asset('tiger.jpg')) as img:
            with open(self.get_dest('tiger-4.jpg'), 'wb') as fp:
                img.save(fp)

            fp = six.BytesIO()
            img.save(fp)
            fp.seek(0)
            self.assertTrue(len(fp.read()) > 0)

    def test_close(self):
        p = self.processor(self.get_asset('tiger.jpg'))
        p.assert_open()
        p.close()
        self.assertRaises(AttributeError, p.assert_open)

        with self.processor(self.get_asset('tiger.jpg')) as img:
            img.assert_open()

        self.assertRaises(AttributeError, img.assert_open)

    def test_crop(self):
        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            p.crop(1, 'smart').save(self.get_dest('crop-smart1'))

        with self.processor(self.get_asset('tiger.jpg')) as p:
            p.crop(1, 'smart').save(self.get_dest('crop-smart2'))

        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            p.crop(1, 'center').save(self.get_dest('crop-center1'))

        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            p.crop(1, -4000, -4000).save(self.get_dest('crop-out1'))

        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            p.crop(1, 4000, 4000).save(self.get_dest('crop-out2'))

        with self.processor(self.get_asset('tiger.jpg')) as p:
            p.crop(150, 50, 500, 400).save(self.get_dest('crop-coord'))

        with self.processor(self.get_asset('tiger.jpg')) as p:
            p.crop(5 / 1, 'center').save(self.get_dest('crop-center2'))

        with self.processor(self.get_asset('tiger.jpg')) as p:
            p.crop(1 / 5, 'center').save(self.get_dest('crop-center3'))

    def test_resize(self):
        with self.processor(self.get_asset('nocomments.gif')) as p:
            p.resize(200, 200).save(self.get_dest('resize1'))

        with self.processor(self.get_asset('beach.jpg')) as p:
            p.resize(400, 400).save(self.get_dest('resize2'))

    def test_thumbnail(self):
        with self.processor(self.get_asset('tiger.jpg')) as p:
            p.thumbnail(500, 500).save(self.get_dest('thumbnail1'))
            self.assertEqual(p.size, (500, 281))

        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            size = p.size
            p.thumbnail(700, 700).save(self.get_dest('thumbnail2'))
            self.assertEqual(size, p.size)

        with self.processor(self.get_asset('mona-lisa.jpg')) as p:
            p.thumbnail(700, 700, upscale=True).save(self.get_dest('thumbnail3'))
            self.assertEqual(p.size, (470, 700))

    def test_rotate(self):
        with self.processor(self.get_asset('beach.jpg')) as p:
            p.rotate(5).save(self.get_dest('rotate'))

    def test_borders(self):
        with self.processor(self.get_asset('beach.jpg')) as p:
            p.add_border(5, 'white').add_border(5, '#c00').save(self.get_dest('border'))


class PillowTests(ProcessorTestCase, TestCase):
    processor = get_processor('pillow')


class WandTests(ProcessorTestCase, TestCase):
    processor = get_processor('wand')
