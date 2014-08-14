# -*- coding: utf-8 -*-
#
# This file is part of Miniature released under the FreeBSD license.
# See the LICENSE for more information.
from setuptools import setup, find_packages

# Get app version
with open('miniature/version.py', 'rb') as fp:
    g = {}
    exec(fp.read(), g)
    version = g['__version__']

# Get package list
packages = find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests'])


# Read README file
def readme():
    with open('README.rst', 'r') as fp:
        return fp.read()

# Setup
setup(
    name='Miniature',
    version=version,
    description='Multi backend image processing and thumbnailer',
    author='Olivier Meunier',
    author_email='olivier@neokraft.net',
    license='FreeBSD',
    url='https://github.com/olivier-m/miniature',
    long_description=readme(),
    keywords='image thumbnail',
    install_requires=[
    ],
    extras_require={
        'pillow': ['pillow'],
        'wand': ['wand'],
        'six': ['six'],
    },
    tests_require=['pillow', 'wand', 'six'],
    test_suite='test',
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
