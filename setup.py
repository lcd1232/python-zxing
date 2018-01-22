#!/usr/bin/env python
 
from distutils.core import setup
import zxing

setup(
    name='zxing',
    version=zxing.__version__,
    description="wrapper for zebra crossing (zxing) barcode library",
    url='http://simplecv.org',
    author='Ingenuitas',
    author_email='public.relations@ingenuitas.com',
    packages=['zxing'],
    requires=['future']
)
