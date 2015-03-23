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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import * 
from PyQt4.QtWebKit import *
from qgis.core import *
from VTMToolBar import VTMToolBar

import psycopg2

import os.path


class VTMMain:

    instance = None

    sqlFilter = '("computed_date_start" IS NULL OR "computed_date_start"<=/**/2015/**/) AND ("computed_date_end" IS NULL OR "computed_date_end">/**/2015/**/)'
    filteredEventsLayersIDs = ['properties_for_qgis20150307001918975', 'properties_for_qgis20150307041406392', 'properties_for_qgis20150317102814809']
    eventsLayerID = 'properties20150212181047441'
    entitiesLayerID = 'entities20150212181047504'
    relationsLayerID = 'related_entities20150303160720006'
    entitiesTypeLayerID = 'entity_types20150306220740482'
    propertiesTypeLayerID = 'properties_types20150317175434094'

    def __init__(self, iface):

        self.plugin_dir = os.path.dirname(__file__)
        
        # Save reference to the QGIS interface
        self.iface = iface
        #self.sqlManager = VTMSqlManager(self.iface)
        VTMMain.instance = self

        self.loaded = False
        self.loadLayers()


    def initGui(self):
        """ Put your code here and remove the pass statement"""

        self.dockwidget = VTMToolBar(self.iface, self)
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea,self.dockwidget)
        self.dockwidget.show()

    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockwidget)


    def loadLayers(self):

        self.filteredEventsLayers = [QgsMapLayerRegistry.instance().mapLayer(layerID) for layerID in self.filteredEventsLayersIDs]
        self.eventsLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsLayerID)
        self.entitiesLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesLayerID)
        self.relationsLayer = QgsMapLayerRegistry.instance().mapLayer(self.relationsLayerID)
        self.propertiesTypeLayer = QgsMapLayerRegistry.instance().mapLayer(self.propertiesTypeLayerID)
        self.entitiesTypeLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesTypeLayerID)

        if not all(self.filteredEventsLayers) or self.eventsLayer is None or self.entitiesLayer is None or self.relationsLayer is None or self.propertiesTypeLayer is None or self.entitiesTypeLayer is None:
            QgsMessageLog.logMessage('Unable to load some needed VTM layers. Plugin will not work. Make sure you opened the provided QGIS project.','VTM Slider')
            return

        self.loaded = True
        QgsMessageLog.logMessage('Loaded all needed layers. Plugin will work.','VTM Slider')


    def getConnection(self):

        ############################################################
        # Get the postgres connection using the eventsLayer uri and credentials
        ############################################################

        connection = None
        
        uri = QgsDataSourceURI( self.eventsLayer.dataProvider().dataSourceUri() )
        connectionInfo = uri.connectionInfo()
        
        host = uri.host()# or os.environ.get('PGHOST')
        port = uri.port()# or os.environ.get('PGPORT')
        database = uri.database()# or os.environ.get('PGDATABASE')
        username = uri.username()# or os.environ.get('PGUSER') or os.environ.get('USER')
        password = uri.password()# or os.environ.get('PGPASSWORD')
        
        try:
            # We try to connect using simply the uri's information (likely to fail if the layer does not store username and password)
            connection = psycopg2.connect( host=host, port=port, database=database, user=username, password=password )
            
        except Exception as e:
            
            # We try to get the credentials
            (ok, username, password) = QgsCredentials.instance().get(connectionInfo.encode('utf-8'), None, None)
            if not ok:
                QgsMessageLog.logMessage('Could not get the credentials. Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings.','VTM Slider')
                return None
            try:
                # We try now to connect using those credentials (host, port, database, username, password )
                connection = psycopg2.connect( host=host, port=port, database=database, user=username, password=password )
                QgsCredentials.instance().put(connectionInfo, username, password)
            except Exception as e:
                QgsMessageLog.logMessage('Could not connect with provided credentials (%s %s %s %s %s). Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings. Error was %s' % (host, port, database, username, password, str(e) ),'VTM Slider')
                return None

        return connection


