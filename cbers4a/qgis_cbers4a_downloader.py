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

import json
import os
from tempfile import gettempdir

from osgeo import gdal

gdal.UseExceptions()

from qgis.core import (Qgis, QgsApplication, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsGeometry, QgsMessageLog,
                       QgsPointXY, QgsProject, QgsRasterLayer, QgsRectangle,
                       QgsSettings, QgsTask)
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtCore import QDate, Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (QAction, QCheckBox, QListWidgetItem,
                                 QPushButton)

from .cbers4a import Search
from .dockcbers4adownloader import DockCbers4aDownloader
from .resources import *

from .provider import Provider

__author__ = "Sandro Klippel"
__copyright__ = "Copyright 2020, Sandro Klippel"
__license__ = "MIT"
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
        self.provider = None
        self.action = None
        self.name = 'CBERS4A Downloader'
        self.about = 'Search and download CBERS4A imagery'
        self.search = None
        self.collections = None
        self.result = None
        self.footprint = QgsRubberBand(iface.mapCanvas(), True)
        self.mux_grid = None
        self.wfi_grid = None
        self.downloading = False
        self.outputfolder = QgsProject.instance().absolutePath() or gettempdir()

    def initProcessing(self):
        self.provider = Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """
        This method is called by QGIS when the main GUI starts up or 
        when the plugin is enabled in the Plugin Manager.
        Only want to register the menu items and toolbar buttons here,
        and connects action with run method.
        """ 
        
        self.initProcessing()

        icon = QIcon(':/plugins/cbers4a/cbers4a.svg')
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
            self.dockwidget.downloadButton.clicked.disconnect(self.start_download)
            # footprint pushbutton
            self.dockwidget.footprint.clicked.disconnect(self.toggle_footprint)

            # close search session
            self.search.close()

        # for raster menu/toolbar
        # self.iface.removePluginRasterMenu(self.name, self.action)
        # self.iface.removeRasterToolBarIcon(self.action)

        # for plugin menu/toolbar
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(self.name, self.action)

        # remove canvas item (footprint)
        self.iface.mapCanvas().scene().removeItem(self.footprint)

        if self.dockwidget is not None:
            self.dockwidget.close()
            self.dockwidget.visibilityChanged.disconnect(self.visibility_changed)
            self.iface.removeDockWidget(self.dockwidget)
            del self.dockwidget

        # remove custom toolbar
        # if self.toolbar is not None:
            # del self.toolbar

        # remove processing provider
        QgsApplication.processingRegistry().removeProvider(self.provider)

        # clean up task
        try:
            del globals()['cbers4a_tasks']
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
                self.dockwidget.footprint.setChecked(False)
                self.footprint.hide()
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
        Return a tuple with current extent and crs
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
        # also update footprint
        self.update_footprint()

    def update_startdate(self, new_date):
        defaults = QgsSettings()
        self.dockwidget.enddate.setDate(new_date.addDays(int(defaults.value("cbers4a/timespan", 30))))
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
        Set collection to search in and valid start and end dates for this collection
        """
        collection_id = self.dockwidget.collection.currentText()
        inpe_collections = {description: id for id, description in self.collections}

        # set collection to search
        self.search.collections([inpe_collections[collection_id]])

        # set valid minimum dates
        mindate = self.collections.get_temporal_extent(inpe_collections[collection_id])[0].split('-')
        year, month, day = int(mindate[0]), int(mindate[1]), int(mindate[2])
        self.dockwidget.startdate.setMinimumDate(QDate(year, month, day))
        self.dockwidget.enddate.setMinimumDate(QDate(year, month, day))

        # set valid maximum dates
        self.dockwidget.startdate.setMaximumDate(QDate.currentDate())
        self.dockwidget.enddate.setMaximumDate(QDate.currentDate())

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
            list_item = QListWidgetItem(icon, str(item.id), self.dockwidget.resultsList)
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
        self.dockwidget.footprint.setChecked(False)
        self.footprint.hide()
        self.dockwidget.footprint.setDisabled(True)
        self.dockwidget.assetsList.clear()
        self.dockwidget.assetsList.setDefaultText('')

    def preview(self, item):
        """
        Preview selected scene
        """
        self.clear_preview()
        item_id = item.text()
        self.dockwidget.webView.setHtml(self.result[item_id].html)
        self.dockwidget.item_id.setText(item_id)
        self.dockwidget.item_date.setText('{0}'.format(self.result[item_id].date))
        self.dockwidget.item_cloudcover.setText('{0:.1f} %'.format(self.result[item_id].cloud_cover))
        self.update_footprint()
        self.dockwidget.footprint.setEnabled(True)
        self.dockwidget.assetsList.setDefaultText('ALL')
        self.dockwidget.assetsList.addItems(self.result[item_id].assets)
        self.dockwidget.tabs.setCurrentIndex(2)
    
    def toggle_download_button(self, tab):
        """
        Enable/disable download button and hide footprint on tab change
        """
        if tab == 2:
            item_id = self.dockwidget.item_id.text()
            credential = self.dockwidget.credential.text()
            if item_id and credential:
                self.dockwidget.downloadButton.setEnabled(True)
            elif self.downloading:
                self.dockwidget.downloadButton.setEnabled(True)
            else:
                self.dockwidget.downloadButton.setDisabled(True)
        else:
            self.dockwidget.footprint.setChecked(False)
            self.footprint.hide()

        # update valid maximum dates on tab change
        self.dockwidget.startdate.setMaximumDate(QDate.currentDate())
        self.dockwidget.enddate.setMaximumDate(QDate.currentDate())

    def start_download(self):
        """
        Start/cancel task to download item asset(s)
        """
        if self.downloading:
            globals()['cbers4a_tasks'].cancel()
        else:
            item_id = self.dockwidget.item_id.text()
            sel_assets = self.dockwidget.assetsList.checkedItems()
            if sel_assets:
                assets = [asset for asset in sel_assets]
            else:
                assets = self.result[item_id].assets
            
            # 
            # create the task variable with global scope
            # workaround for QGIS Issue #28531
            # https://gis.stackexchange.com/questions/296175/issues-with-qgstask-and-task-manager/304801#304801
            #
    
            globals()['cbers4a_tasks'] = QgsTask.fromFunction('Download {0}'.format(item_id), 
            self.download_asset, on_finished=self.download_finished, item_id=item_id, assets=assets)
    
            # self.info('Starting task to download {} asset(s)'.format(item_id), duration=1)
            QgsApplication.taskManager().addTask(globals()['cbers4a_tasks'])
    
            # lock downloading
            self.downloading = True
            self.dockwidget.options.setDisabled(True)
            self.dockwidget.results.setDisabled(True)
            self.dockwidget.downloadButton.setText('Cancel Download')
            self.dockwidget.downloadButton.setStyleSheet('background-color: #ff3336')
            self.dockwidget.assetsList.setDisabled(True)


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
        collection = self.result[item_id].collection
        outdir = self.dockwidget.outputfolder.lineEdit().text() or self.outputfolder
        session = self.search.session
        filenames = {}
        for asset in assets:
            url = self.result[item_id].url(asset)
            filename = url.split("/")[-1]
            outfile = os.path.join(outdir, filename)
            r = session.get(url, params={'email': credential, 'item_id': item_id, 'collection': collection}, stream=True, allow_redirects=True)
            if r.status_code == 200:
                total_size = int(r.headers.get('content-length'))
                size = 0
                with open(outfile + '.part','wb') as f:
                    for ch in r.iter_content(chunk_size=4096): # page size 4kb
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
                os.rename(outfile + '.part', outfile)
                self.log(f'Task {task.description()}:\nDownloaded file: {outfile} ({size} of {total_size} bytes)')
                filenames[asset] = outfile
            else:
                raise Exception('ERROR in ' + url + ' (' + r.reason + ')')

        return {'description': item_id, 'filenames': filenames, 'outdir': outdir}

    def download_finished(self, exception, result=None):
        """
        This is called when download_asset is finished.
        Exception is not None if download_asset raises an exception.
        result is the return value of download_asset.
        """
        
        # VERY SLOW TO DO HERE
        # def __pszXML(nbands):
        #     specband = '\n'.join([f"""<SpectralBand dstBand="{n+1}">\n</SpectralBand>""" for n in range(nbands)])
        #     return f"""<VRTDataset subClass="VRTPansharpenedDataset">
        # <PansharpeningOptions>
        # {specband}
        # </PansharpeningOptions>
        # </VRTDataset>"""

        def __add_images(images, description, outdir, msgbar, check, vrt=True, shown=True):
            if check.isChecked() and vrt:
                pan = images.pop('pan', None) # take out pan
                if len(images) > 1:
                    # stack images in a VRT file if there are more than one image left
                    vrtfile = os.path.join(outdir, description + '.vrt')
                    # to sort in r/g/b/nir order here sort(images.keys, key=lambda k: rgbn[k])
                    _RGBN = {'red': 1, 'green': 2, 'blue': 3, 'nir': 4}
                    images_keys_ordered = sorted(images.keys(), key=lambda k: _RGBN.get(k,5))
                    filenames = [images[k] for k in images_keys_ordered] # filenames list in RGBN order
                    ds = gdal.BuildVRT(vrtfile, filenames, options=gdal.BuildVRTOptions(separate=True, resolution='highest'))
                    for i, bn in enumerate(images_keys_ordered):
                        b = ds.GetRasterBand(i + 1)
                        b.SetDescription(bn)
                    ds.FlushCache()
                    ds = None
                    if pan is None:
                        # nothing to do anymore, add VRT file
                        __add_images({'vrt': vrtfile}, description, outdir, msgbar, check, vrt=False)
                    else:
                        # VERY SLOW TO DO HERE (perhaps as ProcessingProvider?)
                        # nbands = len(images)
                        # if nbands > 2: # may be a setting here for pansharpening choice
                        #     pan_ds = gdal.Open(pan)
                        #     pansharpened_ds = gdal.CreatePansharpenedVRT(__pszXML(nbands), pan_ds.GetRasterBand(1),
                        #     [ds.GetRasterBand(i + 1) for i in range(nbands)])
                        #     pansharpened_filename = os.path.join(outdir, description + '_pansharpened.vrt')
                        #     driver = gdal.GetDriverByName('VRT')
                        #     driver.CreateCopy(pansharpened_filename, pansharpened_ds, 0)
                        #     # add ALL
                        #     __add_images({'pansharpened': pansharpened_filename,
                        #                 'pan': pan, 'vrt': vrtfile}, description, outdir, msgbar, check, vrt=False, shown=False)
                        # else:
                        #     # just add pan and vrt files
                        __add_images({'pan': pan, 'vrt': vrtfile}, description, outdir, msgbar, check, vrt=False)
                else:
                    # do not stack since there are not enough images
                    assert pan is not None # 'pan' should be not 'None' here
                    images.update({'pan': pan}) # restore pan
                    __add_images(images, description, outdir, msgbar, check, vrt=False)
            else:
                for k in images.keys():
                    fn = images[k]
                    name = os.path.basename(fn).split('.')[0]
                    layer = QgsRasterLayer(fn, name)
                    if layer.isValid():
                        QgsProject.instance().addMapLayer(layer)
                        if not shown:
                            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(shown)
                msgbar.dismiss()

        # unlock another downloading
        self.downloading = False
        self.dockwidget.options.setEnabled(True)
        self.dockwidget.results.setEnabled(True)
        self.dockwidget.downloadButton.setText('Download')
        self.dockwidget.downloadButton.setStyleSheet('background-color: None') # restore default background color
        self.dockwidget.assetsList.setEnabled(True)

        if exception is None:
            if result is None:
                self.log('Finished with no exception and no result (probably manually canceled by the user)', level=Qgis.Warning)
            else:
                assets = result['filenames'].keys()
                images = {asset: result['filenames'][asset] for asset in assets if not asset.lower().endswith(('_xml','thumbnail'))}
                if images:
                    # ask to add image(s) to canvas
                    widget = self.iface.messageBar().createMessage(f"Download {result['description']} finished")
                    button = QPushButton(widget)
                    button.setText('Add image(s)')
                    widget.layout().addWidget(button)
                    check = QCheckBox(widget)
                    check.setText('Stack in VRT file')
                    widget.layout().addWidget(check)
                    if len(images) < 2:
                        check.setDisabled(True)
                    button.clicked.connect(lambda: __add_images(images, result['description'], result['outdir'], widget, check))
                    self.iface.messageBar().pushWidget(widget, Qgis.Info)
                else:
                    self.info(f"Download {result['description']} finished")
        else:
            self.log("Exception: {}".format(exception), level=Qgis.Critical)
            raise exception

    def toggle_footprint(self):
        """
        Toggle footprint image view on canvas
        """
        if self.dockwidget.footprint.isChecked():
            self.footprint.show()   
        else:
            self.footprint.hide()

    def update_footprint(self):
        """
        Update image footprint (image extent)
        """
        item_id = self.dockwidget.item_id.text()
        if item_id and self.result is not None:
            try:
                if self.result[item_id].sensor == 'WFI':
                    geojson = self.wfi_grid[self.result[item_id].path_row]
                else:
                    geojson = self.mux_grid[self.result[item_id].path_row] # MUX and WPAN
                qgis_geom = QgsGeometry.fromPolygonXY([[QgsPointXY(pt[0],pt[1]) for pt in geojson['coordinates'][0]]])
            except KeyError: # use bbox
                xmin, ymin, xmax, ymax = self.result[item_id].bbox
                qgis_geom = QgsGeometry.fromRect(QgsRectangle(xmin, ymin, xmax, ymax))
            
            self.footprint.setToGeometry(qgis_geom, QgsCoordinateReferenceSystem('EPSG:4326'))
            defaults = QgsSettings()
            self.footprint.setStrokeColor(defaults.value("cbers4a/colorstroke", QColor(255, 255, 82)))
            self.footprint.setWidth(3)
            self.toggle_footprint()

    def load_grids(self):
        """
        Load CBERS4A MUX and WFI grids
        """
        # json files
        json_mux = os.path.join(self.plugin_dir, 'grid/cbers4a_mux.json')
        json_wfi = os.path.join(self.plugin_dir, 'grid/cbers4a_wfi.json')
        
        # read mux grid
        with open(json_mux) as mux:
            self.mux_grid = json.load(mux)
    
        # read wfi grid
        with open(json_wfi) as wfi:
            self.wfi_grid = json.load(wfi)
    
    def defaults_settings(self):
        """
        Init plugin settings defaults:
            - cbers4a/colorstroke
            - cbers4a/cloudcover
            - cbers4a/credential
            - cbers4a/timespan
            - cbers4a/limit
        """
        s = QgsSettings()
        if not s.contains("cbers4a/colorstroke"):
            s.setValue("cbers4a/colorstroke", QColor(255, 255, 82))
            s.setValue("cbers4a/cloudcover", 10)
            s.setValue("cbers4a/credential", '')
            s.setValue("cbers4a/timespan", 30)
            s.setValue("cbers4a/limit", 100)

    def init(self):
        """
        Fill options, default values and connect triggers of the dockwidget
        """
        # init settings
        self.defaults_settings()

        # init Search instance
        self.search = Search()

        # get collections
        self.collections = self.search.get_collections()
        inpe_collections = {description: id for id, description in self.collections}

        # load grids
        self.load_grids()

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
        self.dockwidget.footprint.clicked.connect(self.toggle_footprint)

        # fill collections combobox
        self.dockwidget.collection.addItems(inpe_collections.keys())

        # set defaults
        defaults = QgsSettings()
        self.dockwidget.cloudcover.setValue(int(defaults.value("cbers4a/cloudcover", 10)))
        self.dockwidget.limit.setValue(int(defaults.value("cbers4a/limit", 100))) 
        self.dockwidget.startdate.setDate(QDate.currentDate().addDays(-int(defaults.value("cbers4a/timespan", 30))))
        self.dockwidget.credential.setText(defaults.value("cbers4a/credential", ''))
        self.update_extent()
        self.update_outputfolder()
        # disable download button
        # self.dockwidget.downloadButton.setDisabled(True)
        # validate credential (seems email) 
        # self.dockwidget.credential.clear()
        # validator = QRegExpValidator(QRegExp("[^@]+@[^@]+\.[^@]+"))
        # self.dockwidget.credential.setValidator(validator)

        # disable footprint pushbutton
        self.dockwidget.footprint.setIcon(QIcon(':/images/themes/default/mActionShowSelectedLayers.svg'))
        self.dockwidget.footprint.setCheckable(True)
        self.dockwidget.footprint.setDisabled(True)

        self.dockwidget.downloadButton.setText('Download')
        self.dockwidget.assetsList.setDefaultText('')
        # start in first tab
        self.dockwidget.tabs.setCurrentIndex(0)
