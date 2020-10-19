#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2020 Sandro Klippel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module documentation goes here
   and here
   and ...
"""

from sys import stderr


class ContextManagerPrintBytes(object):
    """
    docstring
    """

    def __init__(
        self,
        total=None,
        unit=None,
        unit_scale=None,
        desc=None,
        initial=None,
        ascii=None,
    ):
        assert unit == "B"
        self._total = total
        self._desc = desc
        self._initial = initial

    def __enter__(self):
        print(
            "{description}, total size {total} bytes".format(
                description=self._desc, total=self._total
            ),
            file=stderr,
        )
        return PrintBytes(self._initial)

    def __exit__(self, exception_type, exception_val, trace):
        print(file=stderr)
        return True


class PrintBytes(object):
    """
    docstring
    """

    def __init__(self, initial):
        self._totalbytes = initial or 0

    def update(self, b):
        """
        docstring
        """
        self._totalbytes = self._totalbytes + b
        print(
            "Downloading: {x} bytes".format(x=self._totalbytes), end="\r", file=stderr
        )


if __name__ == "__main__":
    pass
