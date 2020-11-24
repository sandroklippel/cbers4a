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
import pathlib
from math import isclose

from osgeo import gdal
from qgis.core import (QgsProcessingAlgorithm, QgsProcessingException,
                       QgsProcessingParameterBand, QgsProcessingParameterCrs,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameters, QgsRasterFileWriter)
from qgis.PyQt.QtCore import QCoreApplication

gdal.UseExceptions()

class ParameterVrtDestination(QgsProcessingParameterRasterDestination):
    """
    Copy from:
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/gdal/buildvrt.py

    """    

    def __init__(self, name, description):
        super().__init__(name, description)

    def clone(self):
        copy = ParameterVrtDestination(self.name(), self.description())
        return copy

    def defaultFileExtension(self):
        return 'vrt'

    def createFileFilter(self):
        return '{} (*.vrt *.VRT)'.format(QCoreApplication.translate("GdalAlgorithm", 'VRT files'))

    def supportedOutputRasterLayerExtensions(self):
        return ['vrt']

    def parameterAsOutputLayer(self, definition, value, context):
        return super(QgsProcessingParameterRasterDestination, self).parameterAsOutputLayer(definition, value, context)

    def isSupportedOutputValue(self, value, context):
        output_path = QgsProcessingParameters.parameterAsOutputLayer(self, value, context)
        if pathlib.Path(output_path).suffix.lower() != '.vrt':
            return False, QCoreApplication.translate("GdalAlgorithm", 'Output filename must use a .vrt extension')
        return True, ''

class RGBNComposite(QgsProcessingAlgorithm):
    """
    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    INPUT_R = 'INPUT_R'
    INPUT_G = 'INPUT_G'
    INPUT_B = 'INPUT_B'
    INPUT_N = 'INPUT_N'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('cbers4a', string)

    def createInstance(self):
        return RGBNComposite()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'rgbncomposite'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('RGBN Composite')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Creates a multiband raster (GDAL VRT) with the bands Red-Green-Blue-NIR.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # INPUTS
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_R, self.tr('Red layer')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_G, self.tr('Green layer')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_B, self.tr('Blue layer')))
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_N, self.tr('NIR layer'), optional = True))

        # OUTPUT
        self.addParameter(ParameterVrtDestination(self.OUTPUT,self.tr('VRT file')))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the values of the parameters

        red_layer = self.parameterAsRasterLayer(parameters, self.INPUT_R, context)
        green_layer = self.parameterAsRasterLayer(parameters, self.INPUT_G, context)
        blue_layer = self.parameterAsRasterLayer(parameters, self.INPUT_B, context)
        nir_layer = self.parameterAsRasterLayer(parameters, self.INPUT_N, context)
        output_file = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        # Throw an exception to indicate and invalid input
        if red_layer is None or not red_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_R))
        if green_layer is None or not green_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_G))
        if blue_layer is None or not blue_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_B))
        
        filenames = [red_layer.dataProvider().dataSourceUri(),
                     green_layer.dataProvider().dataSourceUri(),
                     blue_layer.dataProvider().dataSourceUri()]

        bandnames = ['red', 'green', 'blue']

        if nir_layer is None or not nir_layer.isValid():
            crs_ok = red_layer.crs().authid() == green_layer.crs().authid() == blue_layer.crs().authid()
        else:
            crs_ok = red_layer.crs().authid() == green_layer.crs().authid() == blue_layer.crs().authid() == nir_layer.crs().authid()
            filenames.append(nir_layer.dataProvider().dataSourceUri())
            bandnames.append('nir')

        # Throw an exception if they have different crs
        if not crs_ok:
            raise QgsProcessingException("Layers must have the same CRS!")

        # check if it is canceled
        if feedback.isCanceled():
            return {}

        ds = gdal.BuildVRT(output_file, filenames, options=gdal.BuildVRTOptions(separate=True, resolution='highest'))

        for i, bn in enumerate(bandnames):
            b = ds.GetRasterBand(i + 1)
            b.SetDescription(bn)
        ds.FlushCache()
        ds = None

        return {self.OUTPUT: output_file}

class Pansharpening(QgsProcessingAlgorithm):
    """
    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_PAN = 'INPUT_PAN'
    INPUT_XS = 'INPUT_XS'
    BAND_PAN = 'BAND_PAN'
    BAND_R = 'BAND_R'
    BAND_G = 'BAND_G'
    BAND_B = 'BAND_B'
    BAND_NIR = 'BAND_NIR'
    WEIGHT_R = 'WEIGHT_R'
    WEIGHT_G = 'WEIGHT_G'
    WEIGHT_B = 'WEIGHT_B'
    WEIGHT_NIR = 'WEIGHT_NIR'
    OUT_EXTENT = 'OUT_EXTENT'
    OUT_CRS = 'OUT_CRS'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('cbers4a', string)

    def createInstance(self):
        return Pansharpening()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pansharpening'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Pansharpening')

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Simple Pansharpening by Brovey transformation")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # INPUTS
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_PAN, self.tr('Panchromatic layer')))
        self.addParameter(QgsProcessingParameterBand(self.BAND_PAN, self.tr('Pan Band'), 1, self.INPUT_PAN))

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_XS, self.tr('Multispectral layer')))
        self.addParameter(QgsProcessingParameterBand(self.BAND_R, self.tr('Red Band'), 1, self.INPUT_XS))
        self.addParameter(QgsProcessingParameterBand(self.BAND_G, self.tr('Green Band'), 2, self.INPUT_XS))
        self.addParameter(QgsProcessingParameterBand(self.BAND_B, self.tr('Blue Band'), 3, self.INPUT_XS))
        self.addParameter(QgsProcessingParameterBand(self.BAND_NIR, self.tr('NIR Band'), 0, self.INPUT_XS, optional = True))

        weight_r = QgsProcessingParameterNumber(self.WEIGHT_R, self.tr('Weight Red Band'), 
                                                type=QgsProcessingParameterNumber.Double,
                                                defaultValue=0.25, minValue=0, maxValue=1)
        weight_g = QgsProcessingParameterNumber(self.WEIGHT_G, self.tr('Weight Green Band'), 
                                                type=QgsProcessingParameterNumber.Double,
                                                defaultValue=0.25, minValue=0, maxValue=1)
        weight_b = QgsProcessingParameterNumber(self.WEIGHT_B, self.tr('Weight Blue Band'), 
                                                type=QgsProcessingParameterNumber.Double,
                                                defaultValue=0.25, minValue=0, maxValue=1)
        weight_nir = QgsProcessingParameterNumber(self.WEIGHT_NIR, self.tr('Weight NIR Band'), 
                                                type=QgsProcessingParameterNumber.Double,
                                                defaultValue=0.25, minValue=0, maxValue=1, optional = True)                                                                                                

        weight_r.setMetadata({'widget_wrapper':{'decimals':2}})
        weight_g.setMetadata({'widget_wrapper':{'decimals':2}})
        weight_b.setMetadata({'widget_wrapper':{'decimals':2}})
        weight_nir.setMetadata({'widget_wrapper':{'decimals':2}})

        self.addParameter(weight_r)
        self.addParameter(weight_g)
        self.addParameter(weight_b)
        self.addParameter(weight_nir)

        self.addParameter(QgsProcessingParameterExtent(self.OUT_EXTENT, self.tr('Output extent')))
        self.addParameter(QgsProcessingParameterCrs(self.OUT_CRS,self.tr('Output CRS'), None, optional = True))

        # OUTPUT
        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,self.tr('Output layer')))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the values of the parameters

        pan_layer = self.parameterAsRasterLayer(parameters, self.INPUT_PAN, context)
        pan_band = self.parameterAsInt(parameters, self.BAND_PAN, context)

        xs_layer = self.parameterAsRasterLayer(parameters, self.INPUT_XS, context)
        red_band = self.parameterAsInt(parameters, self.BAND_R, context)
        green_band = self.parameterAsInt(parameters, self.BAND_G, context)
        blue_band = self.parameterAsInt(parameters, self.BAND_B, context)
        nir_band = self.parameterAsInt(parameters, self.BAND_NIR, context)

        weight_r = self.parameterAsDouble(parameters, self.WEIGHT_R, context)
        weight_g = self.parameterAsDouble(parameters, self.WEIGHT_G, context)
        weight_b = self.parameterAsDouble(parameters, self.WEIGHT_B, context)
        weight_nir = self.parameterAsDouble(parameters, self.WEIGHT_NIR, context)

        out_crs = self.parameterAsCrs(parameters, self.OUT_CRS, context)
        if not out_crs.isValid():
            out_crs = pan_layer.crs()

        out_extent = self.parameterAsExtent(parameters, self.OUT_EXTENT, context, crs=out_crs)

        output_file = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        output_format = QgsRasterFileWriter.driverForExtension(os.path.splitext(output_file)[1])
        if not output_format:
            output_format = 'GTiff'

        # check if it is canceled
        if feedback.isCanceled():
            return {}

        # Throw an exception to indicate and invalid input
        if pan_layer is None or not pan_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_PAN))
        if xs_layer is None or not xs_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_XS))
        if out_extent is None or out_extent.isEmpty():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUT_EXTENT))

        # Throw an exception if they have different crs
        if pan_layer.crs().authid() != xs_layer.crs().authid():
            raise QgsProcessingException("The panchromatic and multispectral layers must have the same CRS!")

        # update progress
        feedback.setProgressText('Reading layers.')

        # get layers filenames and open GDAL ds
        pan_fn = pan_layer.dataProvider().dataSourceUri()
        xs_fn = xs_layer.dataProvider().dataSourceUri()
        pan_ds = gdal.Open(pan_fn, gdal.GA_ReadOnly)
        xs_ds = gdal.Open(xs_fn, gdal.GA_ReadOnly)

        # check if it is canceled
        if feedback.isCanceled():
            return {}

        bandnames = ['red','green','blue']
        xs_bands = [xs_ds.GetRasterBand(red_band),
                    xs_ds.GetRasterBand(green_band),
                    xs_ds.GetRasterBand(blue_band)]

        # make template XML and update xs_bands list
        if nir_band == 0:
            total_weight = weight_r + weight_g + weight_b
            if total_weight <= 1 and isclose(total_weight, 1, abs_tol=0.011):
                weights = '{0:.2f},{1:.2f},{2:.2f}'.format(weight_r, weight_g, weight_b)
                feedback.pushInfo(f'Using weights [{weights}] in the pansharpening algorithm.')
                pszXML = f"""<VRTDataset subClass="VRTPansharpenedDataset">
                                <PansharpeningOptions>
                                    <AlgorithmOptions>
                                        <Weights>{weights}</Weights>
                                    </AlgorithmOptions>
                                    <SpectralBand dstBand="1">
                                    </SpectralBand>
                                    <SpectralBand dstBand="2">
                                    </SpectralBand>
                                    <SpectralBand dstBand="3">
                                    </SpectralBand>
                                </PansharpeningOptions>
                             </VRTDataset>"""
            else:
                # ignores supplied weights
                feedback.pushInfo('Invalid weights! They will be ignored.')
                pszXML = f"""<VRTDataset subClass="VRTPansharpenedDataset">
                                <PansharpeningOptions>
                                    <SpectralBand dstBand="1">
                                    </SpectralBand>
                                    <SpectralBand dstBand="2">
                                    </SpectralBand>
                                    <SpectralBand dstBand="3">
                                    </SpectralBand>
                                </PansharpeningOptions>
                             </VRTDataset>"""
            # update progress
            # create pansharpened ds for r/g/b bands
            feedback.setProgressText('Pansharpening r/g/b bands.')
        else:
            total_weight = weight_r + weight_g + weight_b + weight_nir
            if total_weight <= 1 and isclose(total_weight, 1, abs_tol=0.011):
                weights = '{0:.2f},{1:.2f},{2:.2f},{3:.2f}'.format(weight_r, weight_g, weight_b, weight_nir)
                feedback.pushInfo(f'Using weights [{weights}] in the pansharpening algorithm.')
                pszXML = f"""<VRTDataset subClass="VRTPansharpenedDataset">
                                <PansharpeningOptions>
                                    <AlgorithmOptions>
                                        <Weights>{weights}</Weights>
                                    </AlgorithmOptions>
                                    <SpectralBand dstBand="1">
                                    </SpectralBand>
                                    <SpectralBand dstBand="2">
                                    </SpectralBand>
                                    <SpectralBand dstBand="3">
                                    </SpectralBand>
                                    <SpectralBand dstBand="4">
                                    </SpectralBand>
                                </PansharpeningOptions>
                             </VRTDataset>"""
            else:
                # ignores supplied weights
                feedback.pushInfo('Invalid weights! They will be ignored.')
                pszXML = f"""<VRTDataset subClass="VRTPansharpenedDataset">
                                <PansharpeningOptions>
                                    <SpectralBand dstBand="1">
                                    </SpectralBand>
                                    <SpectralBand dstBand="2">
                                    </SpectralBand>
                                    <SpectralBand dstBand="3">
                                    </SpectralBand>
                                    <SpectralBand dstBand="4">
                                    </SpectralBand>
                                </PansharpeningOptions>
                             </VRTDataset>"""
            # update progress
            # create pansharpened ds for r/g/b/nir bands
            feedback.setProgressText('Pansharpening r/g/b/nir bands.')
            xs_bands.append(xs_ds.GetRasterBand(nir_band))
            bandnames.append('nir')

        # create pansharpened GDAL ds
        pansharpened_ds = gdal.CreatePansharpenedVRT(pszXML, pan_ds.GetRasterBand(pan_band), xs_bands)

        # check if it is canceled
        if feedback.isCanceled():
            return {}

        # extent (minX, minY, maxX, maxY) and crs (epsg id)
        output_ext = '{0:.18g} {1:.18g} {2:.18g} {3:.18g}'.format(out_extent.xMinimum(), out_extent.yMinimum(), out_extent.xMaximum(), out_extent.yMaximum())
        output_SRS = out_crs.authid()

        # gdal.Warp
        opts = f'-of {output_format} -t_srs {output_SRS} -te {output_ext}'
        feedback.pushInfo('GDAL Warp options: ' + opts)

        # update progress
        feedback.setProgressText('Creating output file ({}).'.format(output_format))
        ds = gdal.Warp(output_file, pansharpened_ds,  options=opts)

        feedback.setProgressText('Naming bands.')
        for i, bn in enumerate(bandnames):
            b = ds.GetRasterBand(i + 1)
            b.SetDescription(bn)
        ds.FlushCache()
        ds = None

        return {self.OUTPUT: output_file}
