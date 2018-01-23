#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from zxing import __version__ as version

setup(
    name='zxing',
    version=version,
    description="wrapper for zebra crossing (zxing) barcode library",
    url='http://simplecv.org',
    author='Ingenuitas',
    author_email='public.relations@ingenuitas.com',
    packages=['zxing'],
    install_requires=['future'],
)
