#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from urllib.error import URLError
    from urllib.request import urlretrieve
except ImportError:
    from urllib2 import URLError, urlretrieve

from zxing import __version__ as version
from os import access, path, R_OK


def download_java_files():
    files = {'java/javase.jar': 'https://repo1.maven.org/maven2/com/google/zxing/javase/3.3.1/javase-3.3.1.jar',
             'java/core.jar': 'https://repo1.maven.org/maven2/com/google/zxing/core/3.3.1/core-3.3.1.jar',
             'java/jcommander.jar': 'https://repo1.maven.org/maven2/com/beust/jcommander/1.72/jcommander-1.72.jar'}

    for fn, url in files.items():
        p = path.join(path.dirname(__file__), 'zxing', fn)
        if access(p, R_OK):
            print("Already have %s." % p)
        else:
            print("Downloading %s from %s ..." % (p, url))
            try:
                urlretrieve(url, p)
            except URLError as e:
                raise SystemExit(*e.args)
    return list(files.keys())


setup(
    name='zxing',
    version=version,
    description="wrapper for zebra crossing (zxing) barcode library",
    url='http://simplecv.org',
    author='Ingenuitas',
    author_email='public.relations@ingenuitas.com',
    packages=['zxing'],
    package_data = {'zxing': download_java_files()},
    install_requires=['future'],
)
