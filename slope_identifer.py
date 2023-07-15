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

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .slope_identifer_provider import SlopeIndentifierProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class SlopeIndentifierPlugin(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = SlopeIndentifierProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
