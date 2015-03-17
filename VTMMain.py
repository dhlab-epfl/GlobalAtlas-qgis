# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VeniceTimeMachine
                                 A QGIS plugin
 VeniceTimeMachine
                              -------------------
        begin                : 2014-03-13
        copyright            : (C) 2014 by Olivier Dalang
        email                : olivier.dalang@gmail.com
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import * 
from PyQt4.QtWebKit import *
from qgis.core import *
from VTMToolBar import VTMToolBar

import os.path


class VTMMain:

    instance = None

    sqlFilter = '("computed_date_start" IS NULL OR "computed_date_start"<=/**/2015/**/) AND ("computed_date_end" IS NULL OR "computed_date_end">/**/2015/**/)'
    timeManagedLayersIDs = ['properties_for_qgis20150307001918975', 'properties_for_qgis20150307041406392', 'properties_for_qgis20150317102814809']
    eventsLayerID = 'properties20150212181047441'
    entitiesLayerID = 'entities20150212181047504'
    relationsLayerID = 'related_entities20150303160720006'

    def __init__(self, iface):

        self.plugin_dir = os.path.dirname(__file__)
        
        # Save reference to the QGIS interface
        self.iface = iface
        #self.sqlManager = VTMSqlManager(self.iface)
        VTMMain.instance = self

        self.loadLayers()


    def initGui(self):
        """ Put your code here and remove the pass statement"""

        self.dockwidget = VTMToolBar(self.iface, self)
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea,self.dockwidget)
        self.dockwidget.show()

    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockwidget)


    def loadLayers(self):

        self.timeManagedLayers = [QgsMapLayerRegistry.instance().mapLayer(layerID) for layerID in self.timeManagedLayersIDs]
        self.eventsLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsLayerID)
        self.entitiesLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesLayerID)
        self.relationsLayer = QgsMapLayerRegistry.instance().mapLayer(self.relationsLayerID)

        if not all(self.timeManagedLayers) or self.eventsLayer is None or self.entitiesLayer is None or self.relationsLayer is None:
            QgsMessageLog.logMessage('Unable to load some needed VTM layers. Plugin will not work. Make sure you opened the provided QGIS project.','VTM Slider')
            return

        for layer in self.timeManagedLayers:
            layer.committedFeaturesAdded.connect( self.committedFeaturesAdded )

        QgsMessageLog.logMessage('Loaded all needed layers. Plugin will work.','VTM Slider')

    def committedFeaturesAdded(self, layerId, addedFeatures):
        if QgsMessageLog is not None: #bug ? why would QgsMessageLog be None ??!
            QgsMessageLog.logMessage('committedFeaturesAdded','VTM Slider')



