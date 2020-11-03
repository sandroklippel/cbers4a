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

import os
from tempfile import gettempdir

from qgis.core import (Qgis, QgsApplication, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsMessageLog, QgsProject,
                       QgsRasterLayer, QgsTask)
from qgis.PyQt.QtCore import QDate, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QListWidgetItem, QPushButton

from .cbers4a import Search
from .dockcbers4adownloader import DockCbers4aDownloader

__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2020, Sandro Klippel"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Sandro Klippel"
__email__ = "sandroklippel at gmail.com"
__status__ = "Prototype"
__revision__ = '$Format:%H$'


class Cbers4aDownloader:
    """Plugin implementation
    """    

    def __init__(self, iface):
        """
        Constructor

        Args:
            iface (qgis.gui.QgisInterface): a reference to the QGIS GUI interface
        """        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dockwidget = None
        self.action = None
        self.icon = 'cbers4a.svg'
        self.name = 'CBERS4A Downloader'
        self.about = 'Search and download CBERS4A imagery'
        self.search = None
        self.collections = None
        self.result = None
        self.downloading = False
        self.outputfolder = QgsProject.instance().absolutePath() or gettempdir()

    def initGui(self):
        """
        This method is called by QGIS when the main GUI starts up or 
        when the plugin is enabled in the Plugin Manager.
        Only want to register the menu items and toolbar buttons here,
        and connects action with run method.
        """        
        icon = QIcon(os.path.join(self.plugin_dir, self.icon))
        self.action = QAction(icon, self.name, self.iface.mainWindow())
        self.action.setWhatsThis(self.about)
        self.action.setStatusTip(self.about)
        self.action.setCheckable(True)
        self.action.triggered.connect(self.run)

        # for raster menu/toolbar
        # self.iface.addRasterToolBarIcon(self.action)
        # self.iface.addPluginToRasterMenu(self.name, self.action)

        # for plugin menu/toolbar
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.name, self.action)

        # for custom toolbar
        # self.toolbar = self.iface.addToolBar('Plugin')
        # self.toolbar.setObjectName('Plugin')
        # self.toolbar.addAction(self.action)

    def unload(self):
        """
        Will be executed when the plugin is disabled. 
        Either in the Plugin Manager or when QGIS shuts down.
        It removes the previously defined QAction object from
        the menu and remove the plugin icon from the toolbar.
        """

        # disconnect triggers
        if self.search is not None:
            self.iface.mapCanvas().extentsChanged.disconnect(self.update_extent)
            self.iface.mapCanvas().destinationCrsChanged.disconnect(self.update_extent)
            self.dockwidget.startdate.dateChanged.disconnect(self.update_startdate)
            self.dockwidget.enddate.dateChanged.disconnect(self.update_enddate)
            self.iface.projectRead.disconnect(self.update_outputfolder)
            self.iface.newProjectCreated.disconnect(self.update_outputfolder)
            QgsProject.instance().projectSaved.disconnect(self.update_outputfolder)
            self.dockwidget.limit.valueChanged.disconnect(self.update_limit)
            self.dockwidget.cloudcover.valueChanged.disconnect(self.update_cloudcover)
            self.dockwidget.collection.currentIndexChanged.disconnect(self.update_collection)
            self.dockwidget.searchButton.clicked.disconnect(self.do_search)
            self.dockwidget.resultsList.itemClicked.disconnect(self.preview)
            # self.dockwidget.credential.textChanged[str].disconnect(self.credential_changed)
            # self.dockwidget.credential.editingFinished.disconnect(self.credential_filled)
            self.dockwidget.tabs.currentChanged[int].disconnect(self.toggle_download_button)
            self.dockwidget.downloadButton.clicked.connect(self.start_download)

            # close search session
            self.search.close()

        # for raster menu/toolbar
        # self.iface.removePluginRasterMenu(self.name, self.action)
        # self.iface.removeRasterToolBarIcon(self.action)

        # for plugin menu/toolbar
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(self.name, self.action)

        if self.dockwidget is not None:
            self.dockwidget.close()
            self.dockwidget.visibilityChanged.disconnect(self.visibility_changed)
            self.iface.removeDockWidget(self.dockwidget)
            del self.dockwidget

        # remove custom toolbar
        # if self.toolbar is not None:
            # del self.toolbar

        # clean up task
        try:
            del globals()['cbers4a_task']
        except KeyError:
            pass


    def run(self):
        """
        Executes the custom plugin functionality.
        This method is called by the previously defined QAction object (callback), 
        which went into the toolbar icon and the menu entry.
        """
        if self.dockwidget is None:
            self.dockwidget = DockCbers4aDownloader()
            self.iface.addDockWidget(Qt.RightDockWidgetArea , self.dockwidget)
            self.dockwidget.visibilityChanged.connect(self.visibility_changed)
            self.init()
            self.dockwidget.show()
        else:
            if self.dockwidget.isVisible():
                self.dockwidget.hide()
            else:
                self.dockwidget.show()

    def visibility_changed(self, change):
        """
        Change icon checked status with dockwidget visibility
        """
        self.action.setChecked(change)

    def get_canvas_extent(self):
        """
        return a tuple with current extent and crs
        """
        crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        extent = self.iface.mapCanvas().extent()
        return extent, crs

    def update_extent(self):
        """
        Update extent from mapcanvas
        """
        current_extent, current_crs = self.get_canvas_extent()
        output_crs = QgsCoordinateReferenceSystem('EPSG:4326') # WGS84
        transform = QgsCoordinateTransform(current_crs, output_crs, QgsProject.instance())
        extent = transform.transformBoundingBox(current_extent)
        self.dockwidget.north.setText('{0:.6f}'.format(extent.yMaximum()))
        self.dockwidget.south.setText('{0:.6f}'.format(extent.yMinimum()))
        self.dockwidget.east.setText('{0:.6f}'.format(extent.xMaximum()))
        self.dockwidget.west.setText('{0:.6f}'.format(extent.xMinimum()))
        self.search.bbox([extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()])

    def update_startdate(self, new_date):
        self.dockwidget.enddate.setDate(new_date.addDays(3))
        self.search.date(self.dockwidget.startdate.date().toString('yyyy-MM-dd'), self.dockwidget.enddate.date().toString('yyyy-MM-dd'))

    def update_enddate(self, end_date):
        if end_date <= self.dockwidget.startdate.date():
            self.dockwidget.startdate.setDate(end_date.addDays(-1))
        self.search.date(self.dockwidget.startdate.date().toString('yyyy-MM-dd'), self.dockwidget.enddate.date().toString('yyyy-MM-dd'))

    def update_outputfolder(self):
        """
        Update default output folder on new/read project
        """
        self.outputfolder = QgsProject.instance().absolutePath() or gettempdir()
        self.dockwidget.outputfolder.lineEdit().setPlaceholderText(self.outputfolder)

    def update_limit(self):
        """
        Set max number of scenes in the search
        """
        self.search.limit(self.dockwidget.limit.value())

    def update_cloudcover(self):
        """
        Set max cloud cover in the search
        """
        self.search.cloud_cover('<=', self.dockwidget.cloudcover.value())

    def update_collection(self):
        """
        Set collect to search in
        """
        self.search.collections([self.collections[self.dockwidget.collection.currentText()]])

    def do_search(self):
        """
        Run search in INPE STAC Catalog
        """
        self.result = self.search()
        self.dockwidget.resultsList.clear()
        # add items to result list
        # self.dockwidget.resultsList.addItems([str(item) for item in self.result])
        icon = QIcon(":/images/themes/default/mIconRaster.svg")
        for item in self.result:
            list_item = QListWidgetItem(icon, str(item), self.dockwidget.resultsList)
            self.dockwidget.resultsList.addItem(list_item)
        if self.result.complete:
            self.dockwidget.resultsMsg.setText('Returned {0} scenes.'.format(self.result.returned))
        else:
            self.dockwidget.resultsMsg.setText('Returned {0} scenes from {1} matched.'.format(self.result.returned, self.result.matched))
        self.dockwidget.tabs.setCurrentIndex(1)
        self.clear_preview()

    def clear_preview(self):
        """
        Clear preview tab
        """
        self.dockwidget.webView.setHtml('') 
        self.dockwidget.item_id.clear()
        self.dockwidget.item_date.clear()
        self.dockwidget.item_cloudcover.clear()
        self.dockwidget.label.clear()
        self.dockwidget.assetsList.clear()

    def preview(self, item):
        """
        Preview selected scene
        """
        self.clear_preview()
        item_id = item.text()
        self.dockwidget.webView.setHtml(self.result[item_id].html)
        self.dockwidget.item_id.setText(item_id)
        self.dockwidget.item_date.setText('Date: {0}'.format(self.result[item_id].date))
        self.dockwidget.item_cloudcover.setText('Cloud cover: {0:.1f} %'.format(self.result[item_id].cloud_cover))
        self.dockwidget.label.setText('Select assets to download (defaults is all):')
        self.dockwidget.assetsList.addItems(self.result[item_id].assets)
        self.dockwidget.tabs.setCurrentIndex(2)
    
    def toggle_download_button(self, tab):
        """
        Enable/disable download button
        """
        if tab == 2:
            item_id = self.dockwidget.item_id.text()
            credential = self.dockwidget.credential.text()
            if item_id and credential and not self.downloading:
                self.dockwidget.downloadButton.setEnabled(True)
            else:
                self.dockwidget.downloadButton.setDisabled(True)
            # clear asset selection on tab change
            self.dockwidget.assetsList.clearSelection()

    def start_download(self):
        """
        Start task to download item asset(s)
        """

        item_id = self.dockwidget.item_id.text()
        sel_items = self.dockwidget.assetsList.selectedItems()
        if sel_items:
            assets = [asset.text() for asset in sel_items]
        else:
            assets = self.result[item_id].assets
        
        # 
        # create the task variable with global scope
        # workaround for QGIS Issue #28531
        # https://gis.stackexchange.com/questions/296175/issues-with-qgstask-and-task-manager/304801#304801
        #

        globals()['cbers4a_tasks'] = QgsTask.fromFunction('Download {0}'.format(item_id), 
        self.download_asset, on_finished=self.download_finished, item_id=item_id, assets=assets)

        self.info('Starting task to download {} asset(s)'.format(item_id))
        QgsApplication.taskManager().addTask(globals()['cbers4a_tasks'])

        # lock downloading
        self.downloading = True
        self.dockwidget.downloadButton.setDisabled(True)
        self.dockwidget.assetsList.clearSelection()

    def info(self, msg, level=Qgis.Info, duration=5):
        """
        docstring
        """
        self.iface.messageBar().pushMessage(msg, level, duration)

    def log(self, msg, level=Qgis.Info):
        """
        docstring
        """
        QgsMessageLog.logMessage(msg, self.name, level)

    def download_asset(self, task, item_id, assets):
        """
        Task function to download asset(s) for a given item id
        """
        self.log('Started task {}'.format(task.description()))
        credential = self.dockwidget.credential.text()
        outdir = self.dockwidget.outputfolder.lineEdit().text() or self.outputfolder
        session = self.search.session
        result = []
        for asset in assets:
            url = self.result[item_id].url(asset)
            filename = url.split("/")[-1]
            outfile = os.path.join(outdir, filename)
            r = session.get(url, params={'key': credential}, stream=True, allow_redirects=True)
            if r.status_code == 200:
                total_size = int(r.headers.get('content-length'))
                size = 0
                with open(outfile,'wb') as f:
                    for ch in r.iter_content(chunk_size=1024):
                        if ch:
                            f.write(ch)
                            size = size + len(ch)
                            progress = ( size / total_size ) * 100
                            # use task.setProgress to report progress
                            task.setProgress(progress)
                            # check task.isCanceled() to handle cancellation
                            if task.isCanceled():
                                self.log('Task "{name}" was canceled'.format(name=task.description()))
                                return None
                self.log(f'Task {task.description()}:\nDownloaded file: {outfile} ({size} of {total_size} bytes)')
                result.append(outfile)
            else:
                raise Exception('ERROR in ' + url + ' (' + r.reason + ')')

        return result

    def download_finished(self, exception, result=None):
        """
        This is called when download_asset is finished.
        Exception is not None if download_asset raises an exception.
        result is the return value of download_asset.
        """

        def __add_raster_layer(filenames, msgbar, shown=True):
            for fn in filenames:
                name = os.path.basename(fn).split('.')[0]
                layer = QgsRasterLayer(fn, name)
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    if not shown:
                        QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(shown)
            msgbar.dismiss()

        # unlock another downloading
        self.downloading = False
        self.dockwidget.downloadButton.setEnabled(True)

        if exception is None:
            if result is None:
                self.log('Finished with no exception and no result (probably manually canceled by the user)', level=Qgis.Warning)
            else:
                # ask to add layer to canvas
                widget = self.iface.messageBar().createMessage(f"{self.name} finished")
                button = QPushButton(widget)
                button.setText('Add layer(s)')
                button.clicked.connect(lambda: __add_raster_layer(result, widget))
                widget.layout().addWidget(button)
                self.iface.messageBar().pushWidget(widget, Qgis.Info)
        else:
            self.log("Exception: {}".format(exception), level=Qgis.Critical)
            raise exception


    def init(self):
        """
        Fill options, default values and connect triggers of the dockwidget
        """
        # init Search instance
        self.search = Search()

        # get collections
        inpe_collections = self.search.get_collections()
        self.collections = {description: id for id, description in inpe_collections}

        # connect triggers
        self.iface.mapCanvas().extentsChanged.connect(self.update_extent)
        self.iface.mapCanvas().destinationCrsChanged.connect(self.update_extent)
        self.dockwidget.startdate.dateChanged.connect(self.update_startdate)
        self.dockwidget.enddate.dateChanged.connect(self.update_enddate)
        self.iface.projectRead.connect(self.update_outputfolder)
        self.iface.newProjectCreated.connect(self.update_outputfolder)
        QgsProject.instance().projectSaved.connect(self.update_outputfolder)
        self.dockwidget.limit.valueChanged.connect(self.update_limit)
        self.dockwidget.cloudcover.valueChanged.connect(self.update_cloudcover)
        self.dockwidget.collection.currentIndexChanged.connect(self.update_collection)
        self.dockwidget.searchButton.clicked.connect(self.do_search)
        self.dockwidget.resultsList.itemClicked.connect(self.preview)
        # self.dockwidget.credential.textChanged[str].connect(self.credential_changed)
        # self.dockwidget.credential.editingFinished.connect(self.credential_filled)
        self.dockwidget.tabs.currentChanged[int].connect(self.toggle_download_button)
        self.dockwidget.downloadButton.clicked.connect(self.start_download)

        # fill combobox
        self.dockwidget.collection.addItems(self.collections.keys())

        # set defaults
        self.dockwidget.cloudcover.setValue(10)
        self.dockwidget.limit.setValue(100) 
        self.dockwidget.startdate.setDate(QDate.currentDate().addDays(-3))
        self.update_extent()
        self.update_outputfolder()
        # disable download button
        # self.dockwidget.downloadButton.setDisabled(True)
        # validate credential (seems email) 
        # self.dockwidget.credential.clear()
        # validator = QRegExpValidator(QRegExp("[^@]+@[^@]+\.[^@]+"))
        # self.dockwidget.credential.setValidator(validator)
        # start in first tab
        self.dockwidget.tabs.setCurrentIndex(0)
