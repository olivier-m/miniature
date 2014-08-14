# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from __future__ import (print_function, division, absolute_import, unicode_literals)

import sys


def get_processor(name):
    if '.' not in name:
        name = 'miniature.processor.{0}_processor.Processor'.format(name.lower())

    module_name = '.'.join(name.split('.')[0:-1])
    class_name = name.split('.')[-1]

    if module_name not in sys.modules:
        __import__(module_name)

    return getattr(sys.modules[module_name], class_name)
