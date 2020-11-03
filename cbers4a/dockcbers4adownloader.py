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


from qgis.PyQt import QtWidgets
from .dockcbers4adownloaderbase import Ui_DockCbers4aDownloader

__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2020, Sandro Klippel"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Sandro Klippel"
__email__ = "sandroklippel at gmail.com"
__status__ = "Prototype"
__revision__ = '$Format:%H$'


class DockCbers4aDownloader(QtWidgets.QDockWidget, Ui_DockCbers4aDownloader):

    def __init__(self, parent=None):

        super(DockCbers4aDownloader, self).__init__(parent)
        self.setupUi(self)