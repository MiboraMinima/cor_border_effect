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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'LETG, IUEM (Plouzané, FR)'
__date__ = '2023-05-22'
__copyright__ = '(C) 2023 by LETG, IUEM (Plouzané, FR)'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SlopeIndentifier class from file SlopeIndentifier.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .slope_identifer import SlopeIndentifierPlugin
    return SlopeIndentifierPlugin()