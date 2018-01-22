########################################################################
#
#  zxing.py -- a quick and dirty wrapper for zxing for python
#
#  this allows you to send images and get back data from the ZXing
#  library:  https://github.com/zxing/zxing
#

from __future__ import print_function
from enum import Enum
from io import BufferedIOBase
from tempfile import NamedTemporaryFile

from .version import __version__
import subprocess as sp
import re
import os


class BarCodeReader(object):
    cls = "com.google.zxing.client.j2se.CommandLineRunner"

    def __init__(self, classpath=None, java=None):
        self.java = java or 'java'
        if classpath:
            self.classpath = classpath if isinstance(classpath, str) else ':'.join(classpath)
        elif "ZXING_CLASSPATH" in os.environ:
            self.classpath = os.environ.get("ZXING_CLASSPATH", "")
        else:
            self.classpath = os.path.join(os.path.dirname(__file__), 'java', '*')

    def decode(self, files, try_harder=False, possible_formats=None):
        possible_formats = (possible_formats,) if isinstance(possible_formats, str) else possible_formats

        cmd = [self.java, '-cp', self.classpath, self.cls]
        if try_harder:
            cmd.append('--try_harder')
        if possible_formats:
            for pf in possible_formats:
                cmd += ['--possible_formats', pf]

        tmp_files = []
        try:
            if isinstance(files, (list, tuple)):
                for file in files:
                    if isinstance(file, bytes):
                        tmp_file = NamedTemporaryFile()
                        tmp_file.write(file)
                        tmp_file.seek(0)
                        tmp_files.append(tmp_file)
                        cmd.append(tmp_file.name)
            elif isinstance(files, bytes):
                tmp_file = NamedTemporaryFile()
                tmp_file.write(files)
                tmp_file.seek(0)
                tmp_files.append(tmp_file)
                cmd.append(tmp_file.name)
            elif isinstance(files, BufferedIOBase):
                fp = files
                fp.seek(0)
                tmp_file = NamedTemporaryFile()
                while True:
                    data = fp.read(4096)
                    if not data:
                        break
                    tmp_file.write(data)
                tmp_file.seek(0)
                tmp_files.append(tmp_file)
                cmd.append(tmp_file.name)
            else:
                cmd.append(files)

            p = sp.Popen(cmd, stdout=sp.PIPE, universal_newlines=False)
            stdout, stderr = p.communicate()

            if not p.returncode:
                codes = []
                for result in stdout.split("\nfile:"):
                    codes.append(BarCode.parse(result))
                return codes
        finally:
            for tmp_file in tmp_files:
                if hasattr(tmp_file, 'close'):
                    tmp_file.close()


class CLROutputBlock(Enum):
    UNKNOWN = 0
    RAW = 1
    PARSED = 2
    POINTS = 3


class BarCode(object):
    @classmethod
    def parse(cls, zxing_output):
        block = CLROutputBlock.UNKNOWN
        format = type = None
        raw = parsed = b''
        points = []

        for l in zxing_output.splitlines(True):
            if block == CLROutputBlock.UNKNOWN:
                if l.endswith(b': No barcode found\n'):
                    return None
                m = re.search(r"format:\s*([^,]+),\s*type:\s*([^)]+)", l)
                if m:
                    format, type = m.group(1).decode(), m.group(2).decode()
                elif l.startswith(b"Raw result:"):
                    block = CLROutputBlock.RAW
            elif block == CLROutputBlock.RAW:
                if l.startswith(b"Parsed result:"):
                    block = CLROutputBlock.PARSED
                else:
                    raw += l
            elif block == CLROutputBlock.PARSED:
                if re.match(r"Found\s+\d+\s+result\s+points?", l):
                    block = CLROutputBlock.POINTS
                else:
                    parsed += l
            elif block == CLROutputBlock.POINTS:
                m = re.match(r"\s*Point\s*\d+:\s*\(([\d.]+),([\d.]+)\)", l)
                if m:
                    points.append((float(m.group(1)), float(m.group(2))))

        raw = raw[:-1].decode()
        parsed = parsed[:-1].decode()
        return cls(format, type, raw, parsed, points)

    def __init__(self, format, type, raw, parsed, points):
        self.raw = raw
        self.parsed = parsed
        self.format = format
        self.type = type
        self.points = points

    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r}, {!r})'.format(self.__class__.__name__, self.raw, self.parsed, self.format,
                                                         self.type, self.points)
