# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SlopeIndentifier
                                 A QGIS plugin
 This plugin removes border effect on DOD of cliff top boulders (CTD)
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-22
        copyright            : (C) 2023 by LETG, IUEM (Plouzané, FR)
        email                : antoineledoeuff@yahoo.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'LETG, IUEM (Plouzané, FR)'
__date__ = '2023-05-22'
__copyright__ = '(C) 2023 by LETG, IUEM (Plouzané, FR)'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterVectorDestination,
                       QgsRasterLayer,
                       QgsVectorLayer,
                       QgsSpatialIndex,
                       QgsProcessingUtils)
from qgis.analysis import (QgsRasterCalculator,
                           QgsRasterCalculatorEntry)
import processing
import os
import numpy as np
from osgeo import gdal
import re
import geopandas as gpd


class SlopeIndentifierAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT_SLOPE = 'OUTPUT_SLOPE'
    OUTPUT_DX = 'OUTPUT_DX'
    OUTPUT_DY = 'OUTPUT_DY'
    OUTPUT_DXX = 'OUTPUT_DXX'
    OUTPUT_DYY = 'OUTPUT_DYY'
    OUTPUT_DXY = 'OUTPUT_DXY'
    OUTPUT_CHANGES = 'OUTPUT_CHANGES'
    OUTPUT_MASK = 'OUTPUT_MASK'
    OUTPUT_MERGED = 'OUTPUT_MERGED'
    OUTPUT_DOD = 'OUTPUT_DOD'

    def initAlgorithm(self, config):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('DOD to correct'),
                defaultValue=None
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_SLOPE,
                self.tr('General slope extracted from the DOD'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DX,
                self.tr('First order partial derivative dx (E-W slope) raster map'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DY,
                self.tr('first order partial derivative dy (N-S slope) raster map'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DXX,
                self.tr('Second order partial derivative dxx raster map'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DYY,
                self.tr('Second order partial derivative dyy raster map'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DXY,
                self.tr('Second order partial derivative dxy raster map'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_MASK,
                self.tr('Raster mask generated from slope parameters'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_CHANGES,
                self.tr('Identified changes'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_MERGED,
                self.tr('Merged mask'),
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_DOD,
                self.tr('DOD cleaned')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.

        dod = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        dod_slope = self.parameterAsOutputLayer(parameters, self.OUTPUT_SLOPE, context)
        dod_dx = self.parameterAsOutputLayer(parameters, self.OUTPUT_DX, context)
        dod_dy = self.parameterAsOutputLayer(parameters, self.OUTPUT_DY, context)
        dod_dxx = self.parameterAsOutputLayer(parameters, self.OUTPUT_DXX, context)
        dod_dyy = self.parameterAsOutputLayer(parameters, self.OUTPUT_DYY, context)
        dod_dxy = self.parameterAsOutputLayer(parameters, self.OUTPUT_DXY, context)
        changes = self.parameterAsOutputLayer(parameters, self.OUTPUT_CHANGES, context)
        slope_mask = self.parameterAsOutputLayer(parameters, self.OUTPUT_MASK, context)
        mask_merged = self.parameterAsOutputLayer(parameters, self.OUTPUT_MERGED, context)
        dod_cleaned = self.parameterAsOutputLayer(parameters, self.OUTPUT_DOD, context)

        # =========================================
        # DOD Mask blocs
        # =========================================
        # Create mask layer
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Extract changes")

        mask = QgsProcessingUtils.generateTempFilename('mask_layer.tif')
        feedback.pushInfo(f"Generated temp layer is : {mask}")

        entries = []
        ras = QgsRasterCalculatorEntry()
        ras.ref = 'dod@1'
        ras.raster = dod
        ras.bandNumber = 1
        entries.append(ras)

        calc = QgsRasterCalculator(
            f"(dod@1 <= -0.125) OR (dod@1 >= 0.125)",  # Expression
            mask,  # Output
            'GTiff',  # Format
            dod.extent(), dod.width(), dod.height(),  # Extents
            entries  # Les rasters en entrées
        )
        calc.processCalculation()

        # -----------------------------------------
        # Polygonize mask
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Polygonizing")

        params = {
            'INPUT': mask,
            'BAND': 1,
            'FIELD': 'DN',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }

        mask_bloc_pol = processing.run(
            "gdal:polygonize",
            params,
            context=context,
            feedback=feedback
        )
        mask_bloc_pol_lyr = mask_bloc_pol['OUTPUT']

        # -----------------------------------------
        # Extract block
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Get changes in vectorial layer")

        alg_params = {
            'EXPRESSION': '"DN" = 1',
            'INPUT': mask_bloc_pol_lyr,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        block = processing.run('native:extractbyexpression',
                               alg_params,
                               context=context,
                               feedback=feedback)
        block_lyr = block['OUTPUT']

        # -----------------------------------------
        # Delete holes
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Remove holes")

        block_holes = processing.run("native:deleteholes",
                                     {
                                         'INPUT': block_lyr,
                                         'MIN_AREA': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'
                                     },
                                     context=context,
                                     feedback=feedback)
        block_holes_lyr = block_holes['OUTPUT']

        # -----------------------------------------
        # Compute Area
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Computing area")

        alg_params = {
            'FIELD_LENGTH': 20,
            'FIELD_NAME': 'area',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Float
            'FORMULA': '$area*1000',
            'INPUT': block_holes_lyr,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        block_area = processing.run('native:fieldcalculator',
                                    alg_params,
                                    context=context,
                                    feedback=feedback)
        block_area_lyr = block_area['OUTPUT']

        # -----------------------------------------
        # Compute Roundness
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Computing roundness")

        block_round = processing.run("native:roundness",
                                     {
                                         'INPUT': block_area_lyr,
                                         'OUTPUT': 'TEMPORARY_OUTPUT'
                                     },
                                     context=context,
                                     feedback=feedback)
        block_round_lyr = block_round['OUTPUT']

        # -----------------------------------------
        # Extract from indices
        # -----------------------------------------
        # Get area superior to 30 or area <= 30 and roundness >= 0.15
        feedback.pushInfo(" ")
        feedback.pushInfo("Filtering layer")

        # Extract the big part
        alg_params = {
            'EXPRESSION': '"area" >= 30 OR ("roundness" >= 0.4 AND "area" >= 2)',
            'INPUT': block_round_lyr,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        mask_bloc_vec1 = processing.run('native:extractbyexpression',
                                       alg_params,
                                       context=context,
                                       feedback=feedback)['OUTPUT']

        # Remove the rest
        alg_params = {
            'EXPRESSION': 'NOT ("area" <= 120 AND "roundness" <=0.2)',
            'INPUT': mask_bloc_vec1,
            'OUTPUT': changes
        }
        mask_bloc_vec = processing.run('native:extractbyexpression',
                                       alg_params,
                                       context=context,
                                       feedback=feedback)
        mask_bloc_vec_lyr = mask_bloc_vec['OUTPUT']

        # =========================================
        # COMPUTE SLOPE PARAMETERS
        # =========================================
        feedback.pushInfo(" ")
        feedback.pushInfo(f"Computing slope parameter from DOD")

        params = {
            'elevation': dod,
            'format': 0,
            'precision': 0,
            '-a': True,
            '-e': True,
            '-n': False,
            'zscale': 1,
            'min_slope': 0,
            'slope': dod_slope,
            'dx': dod_dx,
            'dy': dod_dy,
            'dxx': dod_dxx,
            'dyy': dod_dyy,
            'dxy': dod_dxy,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_RASTER_FORMAT_META': ''
        }

        slopes_lyr = processing.run(
            "grass7:r.slope.aspect",
            params,
            context=context,
            feedback=feedback
        )

        # -----------------------------------------
        # CREATE MASK LAYER FROM SLOPES
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Generating raster mask layer")

        layers = [
            QgsRasterLayer(slopes_lyr['slope']),
            QgsRasterLayer(slopes_lyr['dx']),
            QgsRasterLayer(slopes_lyr['dy']),
            QgsRasterLayer(slopes_lyr['dxx']),
            QgsRasterLayer(slopes_lyr['dyy']),
            QgsRasterLayer(slopes_lyr['dxy'])
        ]

        # Paramètre de la calculatrice raster
        entries = []
        for idx, layer in enumerate(layers):
            entry = QgsRasterCalculatorEntry()
            entry.ref = f'ras{idx}@1'
            entry.raster = layer
            entry.bandNumber = 1
            entries.append(entry)

        calc = QgsRasterCalculator(
            "(abs('ras0@1')>=45) OR (abs('ras1@1')>=5) OR (abs('ras2@1')>=5) OR (abs('ras3@1')>=150) OR (abs('ras4@1')>=150) OR (abs('ras5@1')>=40)",
            # Expression
            slope_mask,  # Output
            'GTiff',  # Format
            dod.extent(), dod.width(), dod.height(),  # Extents
            entries  # Les rasters en entrées
        )
        calc.processCalculation()

        # --------------------------------------------
        # Plygonize
        # --------------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Polygonizing")

        params = {
            'INPUT': slope_mask,
            'BAND': 1,
            'FIELD': 'DN',
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }

        mask_pol = processing.run(
            "gdal:polygonize",
            params,
            context=context,
            feedback=feedback
        )
        mask_pol_lyr = mask_pol['OUTPUT']

        # -----------------------------------------
        # Extract non slope
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Get relevant value from polygonized layer")

        alg_params = {
            'EXPRESSION': '"DN" = 0',
            'INPUT': mask_pol_lyr,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        poly_filtered = processing.run('native:extractbyexpression',
                                       alg_params,
                                       context=context,
                                       feedback=feedback)['OUTPUT']

        # -----------------------------------------
        # Delete holes
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Remove holes")

        poly_holes = processing.run("native:deleteholes",
                                     {
                                         'INPUT': poly_filtered,
                                         'MIN_AREA': 0.01, 'OUTPUT': 'TEMPORARY_OUTPUT'
                                     },
                                     context=context,
                                     feedback=feedback)["OUTPUT"]

        # -----------------------------------------
        # Difference
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Fix geometry")

        poly_filtered_fix = processing.run(
            "native:fixgeometries",
            {
                'INPUT': poly_holes,
                'METHOD': 1,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        mask_bloc_vec_fix = processing.run(
            "native:fixgeometries",
            {
                'INPUT': mask_bloc_vec_lyr,
                'METHOD': 1,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        # Spatial Index
        feedback.pushInfo(" ")
        feedback.pushInfo("Add spatial index")

        mask_bloc_vec_fix.dataProvider().createSpatialIndex()
        poly_filtered_fix.dataProvider().createSpatialIndex()

        feedback.pushInfo(" ")
        feedback.pushInfo("Difference")

        alg_params = {
            'INPUT': poly_filtered_fix,
            'OVERLAY': mask_bloc_vec_fix,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }

        diff = processing.run("native:difference",
                              alg_params,
                              context=context,
                              feedback=feedback)
        diff_lyr = diff['OUTPUT']

        # -----------------------------------------
        # Merge layers
        # -----------------------------------------

        alg_params = {
            'LAYERS': [diff_lyr, mask_bloc_vec_fix],
            'OUTPUT': mask_merged
        }

        merged = processing.run("native:mergevectorlayers",
                                alg_params,
                                context=context,
                                feedback=feedback)["OUTPUT"]

        # -----------------------------------------
        # CLIP DOD BY MASK
        # -----------------------------------------
        feedback.pushInfo(" ")
        feedback.pushInfo("Clip original DOD by mask")

        params = {
            'INPUT': dod,
            'MASK': merged,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'TARGET_EXTENT': None,
            'NODATA': None,
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'KEEP_RESOLUTION': False,
            'SET_RESOLUTION': False,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'MULTITHREADING': False,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'EXTRA': '',
            'OUTPUT': dod_cleaned
        }

        dod_clip = processing.run(
            "gdal:cliprasterbymasklayer",
            params,
            context=context,
            feedback=feedback
        )
        dod_clip_lyr = dod_clip['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {
            self.OUTPUT_CHANGES: mask_bloc_vec_lyr,
            self.OUTPUT_DX: dod_dx,
            self.OUTPUT_DY: dod_dy,
            self.OUTPUT_DXX: dod_dxx,
            self.OUTPUT_DYY: dod_dyy,
            self.OUTPUT_DXY: dod_dxy,
            self.OUTPUT_MASK: slope_mask,
            self.OUTPUT_MERGED: merged,
            self.OUTPUT_DOD: dod_clip_lyr
        }

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Remove border effect'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'DOD processing'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SlopeIndentifierAlgorithm()
