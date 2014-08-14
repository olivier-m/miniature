=========
Miniature
=========

Miniature is two tools in one:

- A library providing helpers for simple image manipulation with multiple backends
- A optional Django application for easy thumbnail management

Backends
========

Miniature comes with two supported backends: `Pillow <http://pillow.readthedocs.org/>`_ and
`Wand <http://docs.wand-py.org/>`_.

Installation
============

To install Miniature with Pillow backend if you don't have Django installed::

  pip install "miniature[pillow,six]"

With wand backend if you don't have Django installed::

  pip install "miniature[wand,six]"

If you plan to use Miniature with Django you can omit the "six" dependency::

  pip install "miniature[pillow]"


The library
===========

Miniature provides common functions to manipulate images. First thing to do is to load your
processing class::

  from miniature.processor import get_processor

  Processor = get_processor('pillow')

``get_processor`` will automatically load ``miniature.processor.pillow_processor`` and return
its ``Processor`` class. You could pass a full python path as a string to load any other processor.
You can of course also load your own processor class in a traditional way.

Once you have your processor class you can work on images::

  with Processor('my-image.jpg') as p:
      p.thumbnail(200, 200).save('my-image-mini.jpg')

Note that all image operation returns the processor instance allowing you to chain operations in
a big and ugly one line operation.

save(file, [format], \*\*options)
---------------------------------

Save the image in ``file``. ``file`` could be a file name or a file descriptor. ``format`` should be
an available format. If not provided the extension of the file name (if any) is used or the original
format of the image. Other arguments are passed to the internal save method. You could pass
``quality`` for JPEG images.

close()
-------

Closes the image resource and the associated file descriptor. You don't have to call this method
if you use the processor as a context manager.

set_background(color)
---------------------

Changes the image background color::

  p.set_background('#fff')

crop(\*args)
------------

Crops the image using variable specs.

To crop with coordinates::

  p.crop(10, 20, 50, 70)

To crop with a ratio and a position::

  p.crop(1/2, 'center')

Position could be: **center**, **top-left**, **top-right**, **bottom-right**, **bottom-left**.

To crop with a ratio a a position offset::

  p.crop(1, '-50%', 20)

Offsets are dimensions moving the cropped section from the centre of the image. They could be
percentage or integer (for pixels).

Finally to let the processor determine where to move the cropped zone, you can ask him to be smart
(what it sometime fails to be, let's face it)::

  p.crop(16/9, 'smart')

resize(width, height)
---------------------

Well, I think it's obvious.

thumbnail(width, height)
------------------------

Creates a thumbnail of the image while keeping aspect ratio. You can pass the ``upscale`` option
with ``True`` value to force the image size even when it's smaller than provided dimensions
(default is ``False``).

rotate(angle)
-------------

Rotates the image in a counter clockwise direction following the provided ``angle``.

add_border(width, color)
------------------------

Adds a border of provided ``width`` and ``color`` around image.


Django Application
==================

To be coded and documented.
