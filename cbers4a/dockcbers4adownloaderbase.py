# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cbers4a/ui/dockcbers4adownloader.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockCbers4aDownloader(object):
    def setupUi(self, DockCbers4aDownloader):
        DockCbers4aDownloader.setObjectName("DockCbers4aDownloader")
        DockCbers4aDownloader.resize(360, 592)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DockCbers4aDownloader.sizePolicy().hasHeightForWidth())
        DockCbers4aDownloader.setSizePolicy(sizePolicy)
        DockCbers4aDownloader.setMinimumSize(QtCore.QSize(360, 82))
        DockCbers4aDownloader.setMaximumSize(QtCore.QSize(360, 524287))
        DockCbers4aDownloader.setFloating(True)
        DockCbers4aDownloader.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        DockCbers4aDownloader.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.tabs = QtWidgets.QTabWidget(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setMinimumSize(QtCore.QSize(280, 0))
        font = QtGui.QFont()
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.tabs.setFont(font)
        self.tabs.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabs.setElideMode(QtCore.Qt.ElideNone)
        self.tabs.setObjectName("tabs")
        self.options = QtWidgets.QWidget()
        self.options.setObjectName("options")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.options)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_7 = QtWidgets.QFrame(self.options)
        self.frame_7.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(self.frame_7)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.collection = QtWidgets.QComboBox(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.collection.sizePolicy().hasHeightForWidth())
        self.collection.setSizePolicy(sizePolicy)
        self.collection.setMinimumSize(QtCore.QSize(0, 0))
        self.collection.setObjectName("collection")
        self.horizontalLayout.addWidget(self.collection)
        self.verticalLayout_6.addWidget(self.frame_7)
        self.frame_3 = QtWidgets.QFrame(self.options)
        self.frame_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        spacerItem = QtWidgets.QSpacerItem(34, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout_4.addWidget(self.label_9, 0, 1, 1, 1)
        self.north = QtWidgets.QLabel(self.frame_3)
        self.north.setMinimumSize(QtCore.QSize(100, 20))
        self.north.setMaximumSize(QtCore.QSize(100, 20))
        self.north.setFrameShape(QtWidgets.QFrame.Box)
        self.north.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.north.setLineWidth(1)
        self.north.setMidLineWidth(0)
        self.north.setText("")
        self.north.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.north.setObjectName("north")
        self.gridLayout_4.addWidget(self.north, 0, 2, 1, 2)
        self.label_10 = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_10.setObjectName("label_10")
        self.gridLayout_4.addWidget(self.label_10, 1, 0, 1, 1)
        self.west = QtWidgets.QLabel(self.frame_3)
        self.west.setMinimumSize(QtCore.QSize(100, 20))
        self.west.setMaximumSize(QtCore.QSize(100, 20))
        self.west.setFrameShape(QtWidgets.QFrame.Box)
        self.west.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.west.setText("")
        self.west.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.west.setObjectName("west")
        self.gridLayout_4.addWidget(self.west, 1, 1, 1, 2)
        self.label_11 = QtWidgets.QLabel(self.frame_3)
        self.label_11.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 1, 3, 1, 1)
        self.east = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.east.sizePolicy().hasHeightForWidth())
        self.east.setSizePolicy(sizePolicy)
        self.east.setMinimumSize(QtCore.QSize(100, 20))
        self.east.setMaximumSize(QtCore.QSize(100, 20))
        self.east.setFrameShape(QtWidgets.QFrame.Box)
        self.east.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.east.setText("")
        self.east.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.east.setObjectName("east")
        self.gridLayout_4.addWidget(self.east, 1, 4, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(34, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.frame_3)
        self.label_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 2, 1, 1, 1)
        self.south = QtWidgets.QLabel(self.frame_3)
        self.south.setMinimumSize(QtCore.QSize(100, 20))
        self.south.setMaximumSize(QtCore.QSize(100, 20))
        self.south.setFrameShape(QtWidgets.QFrame.Box)
        self.south.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.south.setText("")
        self.south.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.south.setObjectName("south")
        self.gridLayout_4.addWidget(self.south, 2, 2, 1, 2)
        self.verticalLayout_6.addWidget(self.frame_3)
        self.frame = QtWidgets.QFrame(self.options)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.enddate = QtWidgets.QDateEdit(self.frame)
        self.enddate.setCalendarPopup(True)
        self.enddate.setObjectName("enddate")
        self.gridLayout_2.addWidget(self.enddate, 1, 2, 1, 1)
        self.startdate = QtWidgets.QDateEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startdate.sizePolicy().hasHeightForWidth())
        self.startdate.setSizePolicy(sizePolicy)
        self.startdate.setCalendarPopup(True)
        self.startdate.setObjectName("startdate")
        self.gridLayout_2.addWidget(self.startdate, 0, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 0, 1, 1, 1)
        self.verticalLayout_6.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.options)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.cloudcover = QtWidgets.QSpinBox(self.frame_2)
        self.cloudcover.setProperty("value", 5)
        self.cloudcover.setObjectName("cloudcover")
        self.gridLayout_3.addWidget(self.cloudcover, 0, 2, 1, 1)
        self.limit = QtWidgets.QSpinBox(self.frame_2)
        self.limit.setMinimum(1)
        self.limit.setMaximum(100)
        self.limit.setProperty("value", 5)
        self.limit.setObjectName("limit")
        self.gridLayout_3.addWidget(self.limit, 1, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem3, 1, 1, 1, 1)
        self.verticalLayout_6.addWidget(self.frame_2)
        self.frame_5 = QtWidgets.QFrame(self.options)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_8 = QtWidgets.QLabel(self.frame_5)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_4.addWidget(self.label_8)
        self.credential = gui.QgsPasswordLineEdit(self.frame_5)
        self.credential.setShowLockIcon(False)
        self.credential.setObjectName("credential")
        self.verticalLayout_4.addWidget(self.credential)
        self.verticalLayout_6.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(self.options)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.frame_6)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.outputfolder = gui.QgsFileWidget(self.frame_6)
        self.outputfolder.setAutoFillBackground(False)
        self.outputfolder.setFileWidgetButtonVisible(True)
        self.outputfolder.setDefaultRoot("")
        self.outputfolder.setStorageMode(gui.QgsFileWidget.GetDirectory)
        self.outputfolder.setObjectName("outputfolder")
        self.verticalLayout_2.addWidget(self.outputfolder)
        self.verticalLayout_6.addWidget(self.frame_6)
        self.searchButton = QtWidgets.QPushButton(self.options)
        self.searchButton.setObjectName("searchButton")
        self.verticalLayout_6.addWidget(self.searchButton)
        self.tabs.addTab(self.options, "")
        self.results = QtWidgets.QWidget()
        self.results.setObjectName("results")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.results)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_13 = QtWidgets.QLabel(self.results)
        self.label_13.setObjectName("label_13")
        self.verticalLayout_3.addWidget(self.label_13)
        self.resultsList = QtWidgets.QListWidget(self.results)
        self.resultsList.setFrameShape(QtWidgets.QFrame.Box)
        self.resultsList.setObjectName("resultsList")
        self.verticalLayout_3.addWidget(self.resultsList)
        self.resultsMsg = QtWidgets.QLabel(self.results)
        self.resultsMsg.setText("")
        self.resultsMsg.setObjectName("resultsMsg")
        self.verticalLayout_3.addWidget(self.resultsMsg)
        self.tabs.addTab(self.results, "")
        self.preview = QtWidgets.QWidget()
        self.preview.setObjectName("preview")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.preview)
        self.verticalLayout.setObjectName("verticalLayout")
        self.item_id = QtWidgets.QLabel(self.preview)
        self.item_id.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_id.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.item_id.setText("")
        self.item_id.setAlignment(QtCore.Qt.AlignCenter)
        self.item_id.setObjectName("item_id")
        self.verticalLayout.addWidget(self.item_id)
        self.webView = QtWebKitWidgets.QWebView(self.preview)
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.frame_4 = QtWidgets.QFrame(self.preview)
        self.frame_4.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.item_date = QtWidgets.QLabel(self.frame_4)
        self.item_date.setMaximumSize(QtCore.QSize(106, 16777215))
        self.item_date.setAutoFillBackground(False)
        self.item_date.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_date.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.item_date.setText("")
        self.item_date.setAlignment(QtCore.Qt.AlignCenter)
        self.item_date.setObjectName("item_date")
        self.horizontalLayout_2.addWidget(self.item_date)
        self.item_cloudcover = QtWidgets.QLabel(self.frame_4)
        self.item_cloudcover.setMaximumSize(QtCore.QSize(106, 16777215))
        self.item_cloudcover.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_cloudcover.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.item_cloudcover.setText("")
        self.item_cloudcover.setAlignment(QtCore.Qt.AlignCenter)
        self.item_cloudcover.setObjectName("item_cloudcover")
        self.horizontalLayout_2.addWidget(self.item_cloudcover)
        self.footprint = QtWidgets.QPushButton(self.frame_4)
        self.footprint.setMaximumSize(QtCore.QSize(106, 16777215))
        self.footprint.setCheckable(True)
        self.footprint.setObjectName("footprint")
        self.horizontalLayout_2.addWidget(self.footprint)
        self.verticalLayout.addWidget(self.frame_4)
        self.label = QtWidgets.QLabel(self.preview)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.assetsList = gui.QgsCheckableComboBox(self.preview)
        self.assetsList.setObjectName("assetsList")
        self.verticalLayout.addWidget(self.assetsList)
        self.downloadButton = QtWidgets.QPushButton(self.preview)
        self.downloadButton.setObjectName("downloadButton")
        self.verticalLayout.addWidget(self.downloadButton)
        self.tabs.addTab(self.preview, "")
        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)
        DockCbers4aDownloader.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockCbers4aDownloader)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockCbers4aDownloader)
        DockCbers4aDownloader.setTabOrder(self.tabs, self.collection)
        DockCbers4aDownloader.setTabOrder(self.collection, self.startdate)
        DockCbers4aDownloader.setTabOrder(self.startdate, self.enddate)
        DockCbers4aDownloader.setTabOrder(self.enddate, self.cloudcover)
        DockCbers4aDownloader.setTabOrder(self.cloudcover, self.limit)
        DockCbers4aDownloader.setTabOrder(self.limit, self.credential)
        DockCbers4aDownloader.setTabOrder(self.credential, self.searchButton)
        DockCbers4aDownloader.setTabOrder(self.searchButton, self.resultsList)
        DockCbers4aDownloader.setTabOrder(self.resultsList, self.webView)
        DockCbers4aDownloader.setTabOrder(self.webView, self.footprint)
        DockCbers4aDownloader.setTabOrder(self.footprint, self.assetsList)
        DockCbers4aDownloader.setTabOrder(self.assetsList, self.downloadButton)

    def retranslateUi(self, DockCbers4aDownloader):
        _translate = QtCore.QCoreApplication.translate
        DockCbers4aDownloader.setWindowTitle(_translate("DockCbers4aDownloader", "Search and Download CBERS4A Imagery"))
        self.label_3.setText(_translate("DockCbers4aDownloader", "Dataset:"))
        self.label_9.setText(_translate("DockCbers4aDownloader", "North:"))
        self.label_10.setText(_translate("DockCbers4aDownloader", "West:"))
        self.label_11.setText(_translate("DockCbers4aDownloader", "East:"))
        self.label_12.setText(_translate("DockCbers4aDownloader", "South:"))
        self.label_2.setText(_translate("DockCbers4aDownloader", "The start date:"))
        self.enddate.setDisplayFormat(_translate("DockCbers4aDownloader", "yyyy-MM-dd"))
        self.startdate.setDisplayFormat(_translate("DockCbers4aDownloader", "yyyy-MM-dd"))
        self.label_4.setText(_translate("DockCbers4aDownloader", "The end date:"))
        self.cloudcover.setSuffix(_translate("DockCbers4aDownloader", "%"))
        self.label_5.setText(_translate("DockCbers4aDownloader", "Cloud coverage (max):"))
        self.label_6.setText(_translate("DockCbers4aDownloader", "Number of scenes (max):"))
        self.label_8.setText(_translate("DockCbers4aDownloader", "Credential (only required to download):"))
        self.credential.setToolTip(_translate("DockCbers4aDownloader", "Email registered at http://www2.dgi.inpe.br/catalogo/explore."))
        self.credential.setPlaceholderText(_translate("DockCbers4aDownloader", "someone@somewhere.com"))
        self.label_7.setText(_translate("DockCbers4aDownloader", "Output folder:"))
        self.outputfolder.setDialogTitle(_translate("DockCbers4aDownloader", "Output folder"))
        self.searchButton.setText(_translate("DockCbers4aDownloader", "Search"))
        self.tabs.setTabText(self.tabs.indexOf(self.options), _translate("DockCbers4aDownloader", "Options"))
        self.label_13.setText(_translate("DockCbers4aDownloader", "Click on a scene to preview it."))
        self.tabs.setTabText(self.tabs.indexOf(self.results), _translate("DockCbers4aDownloader", "Results"))
        self.item_date.setToolTip(_translate("DockCbers4aDownloader", "The acquisition date."))
        self.item_cloudcover.setToolTip(_translate("DockCbers4aDownloader", "Cloud coverage."))
        self.footprint.setToolTip(_translate("DockCbers4aDownloader", "Shows the image extent."))
        self.footprint.setText(_translate("DockCbers4aDownloader", "Footprint"))
        self.label.setText(_translate("DockCbers4aDownloader", "Assets to download:"))
        self.assetsList.setDefaultText(_translate("DockCbers4aDownloader", "ALL"))
        self.downloadButton.setText(_translate("DockCbers4aDownloader", "Download"))
        self.tabs.setTabText(self.tabs.indexOf(self.preview), _translate("DockCbers4aDownloader", "Preview"))

from PyQt5 import QtWebKitWidgets
from qgis import gui
