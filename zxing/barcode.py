#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import re
import subprocess
from io import BufferedIOBase
from tempfile import NamedTemporaryFile

try:
    from future.utils import python_2_unicode_compatible
except ImportError:
    def python_2_unicode_compatible(cls):
        return cls
    # Issues with setup.py needed to import module but the `future` dependency hasn't been installed yet.

logger = logging.getLogger(__name__)


class BarCodeReader(object):
    location = ""
    command = "java"
    libs = ["javase.jar", "core.jar", "jcommander.jar"]
    args = ["-cp", "LIBS", "com.google.zxing.client.j2se.CommandLineRunner"]

    def __init__(self, path=None):
        if path:
            self.location = path
        elif os.environ.get("ZXING_LIBRARY"):
            self.location = os.environ["ZXING_LIBRARY"]
        else:
            self.location = os.path.join(os.path.dirname(__file__), 'java')

    def decode(self, files, try_harder=False, qr_only=False):
        cmd = [self.command]
        cmd += self.args[:]  # copy arg values
        if try_harder is True:
            cmd.append("--try_harder")
        if qr_only is True:
            cmd.append("--possibleFormats=QR_CODE")

        libraries = [self.location + "/" + l for l in self.libs]

        cmd = [c if c != "LIBS" else os.pathsep.join(libraries) for c in cmd]

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

            stdout, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True).communicate()
            codes = []
            file_results = stdout.split("\nfile:")
            for result in file_results:
                lines = stdout.split("\n")
                if re.search("No barcode found", lines[0]):
                    codes.append(None)
                    continue

                codes.append(BarCode(result))

            return codes
        finally:
            for tmp_file in tmp_files:
                if hasattr(tmp_file, 'close'):
                    tmp_file.close()


# this is the barcode class which has
class BarCode(object):
    format = ""
    points = []
    data = ""
    raw = ""

    def __init__(self, zxing_output):
        lines = zxing_output.split("\n")
        raw_block = False
        parsed_block = False
        point_block = False

        self.points = []
        for line in lines:
            m = re.search("format:\s([^,]+)", line)
            if not raw_block and not parsed_block and not point_block and m:
                self.format = m.group(1)
                continue

            if not raw_block and not parsed_block and not point_block and line == "Raw result:":
                raw_block = True
                continue

            if raw_block and line != "Parsed result:":
                self.raw += line
                continue

            if raw_block and line == "Parsed result:":
                raw_block = False
                parsed_block = True
                continue

            if parsed_block and not re.match("Found\s\d\sresult\spoints", line):
                self.data += line
                continue

            if parsed_block and re.match("Found\s\d\sresult\spoints", line):
                parsed_block = False
                point_block = True
                continue

            if point_block:
                m = re.search("Point\s(\d+):\s\(([\d.]+),([\d.]+)\)", line)
                if m:
                    self.points.append((float(m.group(2)), float(m.group(3))))

    @python_2_unicode_compatible
    def __str__(self):
        return ""

    def __repr__(self):
        return "<class '{0}'>".format(self.__class__.__name__, )
