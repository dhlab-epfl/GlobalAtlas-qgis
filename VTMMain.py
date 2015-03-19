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
import psycopg2

from qgis.core import *
from VTMToolBar import VTMToolBar

import os.path


class VTMMain:

    instance = None

    sqlFilter = '("computed_date_start" IS NULL OR "computed_date_start"<=/**/2015/**/) AND ("computed_date_end" IS NULL OR "computed_date_end">/**/2015/**/)'
    filteredEventsLayersIDs = ['properties_for_qgis20150307001918975', 'properties_for_qgis20150307041406392', 'properties_for_qgis20150317102814809']
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
 
        # Disconnect the signals as well
        for layer in self.filteredEventsLayers:
            try:
                layer.committedFeaturesAdded.disconnect()
                layer.committedFeaturesRemoved.disconnect()
                layer.committedAttributeValuesChanges.disconnect()
                layer.editingStopped.disconnect()
            except Exception, e:
                pass
        try:
            self.eventsLayer.committedFeaturesAdded.disconnect()
            self.eventsLayer.committedFeaturesRemoved.disconnect()
            self.eventsLayer.committedAttributeValuesChanges.disconnect()
            self.eventsLayer.editingStopped.disconnect()
        except Exception, e:
            pass


    def loadLayers(self):


        ############################################################
        # Get the references to the layers using their IDs
        ############################################################

        self.filteredEventsLayers = [QgsMapLayerRegistry.instance().mapLayer(layerID) for layerID in self.filteredEventsLayersIDs]
        self.eventsLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsLayerID)
        self.entitiesLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesLayerID)
        self.relationsLayer = QgsMapLayerRegistry.instance().mapLayer(self.relationsLayerID)

        if not all(self.filteredEventsLayers) or self.eventsLayer is None or self.entitiesLayer is None or self.relationsLayer is None:
            QgsMessageLog.logMessage('Unable to load some needed VTM layers. Plugin will not work. Make sure you opened the provided QGIS project.','VTM Slider')
            return


        ############################################################
        # Get the postgres connection using the eventsLayer uri and credentials
        ############################################################

        uri = QgsDataSourceURI( self.eventsLayer.dataProvider().dataSourceUri() )
        connectionInfo = uri.connectionInfo()

        host = uri.host()# or os.environ.get('PGHOST')
        port = uri.port()# or os.environ.get('PGPORT')
        database = uri.database()# or os.environ.get('PGDATABASE')
        username = uri.username()# or os.environ.get('PGUSER') or os.environ.get('USER')
        password = uri.password()# or os.environ.get('PGPASSWORD')

        try:
            # We try to connect using simply the uri's information (likely to fail if the layer does not store username and password)
            self.connection = psycopg2.connect( host=host, port=port, database=database, user=username, password=password )

        except Exception as e:
            # If it failed, we get the username and password using QgsCredentials
            try:

                # We try to get the credentials
                (ok, username, password) = QgsCredentials.instance().get(connectionInfo.encode('utf-8'), None, None)
                if not ok:
                    raise ConnectionError()
                try:
                    # We try now to connect using those credentials% (host, port, database, username, password )
                    self.connection = psycopg2.connect( host=host, port=port, database=database, user=username, password=password )
                    QgsCredentials.instance().put(connectionInfo, username, password)
                except Exception as e:
                    QgsMessageLog.logMessage('Could not connect with provided credentials (%s %s %s %s %s). Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings.' % (host, port, database, username, password ),'VTM Slider')
                    return
    
            except Exception as e:
                QgsMessageLog.logMessage('Could not get the credentials. Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings.','VTM Slider')
                return


        ############################################################
        # If everything worked, connect the signals to make the post processing queries
        ############################################################

        self.propertiesTriggeringPostProcessing = []

        # Signals for insert of events
        for layer in self.filteredEventsLayers:
            layer.committedFeaturesAdded.connect( self.committedFeaturesAdded )
            layer.committedAttributeValuesChanges.connect( self.committedAttributeValuesChanges )
            layer.committedFeaturesRemoved.connect( self.committedFeaturesRemoved )
            layer.editingStopped.connect( self.editingStopped )

        self.eventsLayer.committedFeaturesAdded.connect( self.committedFeaturesAdded )
        self.eventsLayer.committedAttributeValuesChanges.connect( self.committedAttributeValuesChanges )
        self.eventsLayer.committedFeaturesRemoved.connect( self.committedFeaturesRemoved )
        self.eventsLayer.editingStopped.connect( self.editingStopped )


        QgsMessageLog.logMessage('Loaded all needed layers. Plugin will work.','VTM Slider')



    def committedFeaturesAdded(self, layerId, addedFeatures):
        QgsMessageLog.logMessage( 'committedFeaturesAdded' , 'VTM Slider'  )
        for feat in addedFeatures:
            QgsMessageLog.logMessage( 'ID %s' % str(feat.id()), 'VTM Slider'  )
            QgsMessageLog.logMessage( 'ATTR %s' % str(feat.attributes()), 'VTM Slider'  )
            self.propertiesTriggeringPostProcessing.append( [feat.attribute('entity_id'),feat.attribute('property_type_id')] )
        

    def committedAttributeValuesChanges(self, layerId, changedAttributesValues):
        QgsMessageLog.logMessage( 'committedAttributeValuesChanges' , 'VTM Slider'  )
        for fid, attrMap in changedAttributesValues:
            QgsMessageLog.logMessage( 'ID %s' % str(fid), 'VTM Slider'  )
            QgsMessageLog.logMessage( 'ATTR %s' % str(attrMap), 'VTM Slider'  )            
            #self.propertiesTriggeringPostProcessing.append( fid )


    def committedFeaturesRemoved(self, layerId, deletedFeaturesIds):            
        QgsMessageLog.logMessage( 'committedFeaturesRemoved' , 'VTM Slider'  )
        for featId in deletedFeaturesIds:
            QgsMessageLog.logMessage( 'ID %s' % str(featId), 'VTM Slider'  )
            #self.propertiesTriggeringPostProcessing.append( featId )
        


    def editingStopped(self):
        QgsMessageLog.logMessage( 'editingStopped triggered', 'VTM Slider'  )
        
        #global os

        #cur = self.connection.cursor()

        #sql = open( os.path.join( os.path.dirname(__file__),'sql','compute_dates.sql') ).read()

        #QgsMessageLog.logMessage( 'sql query loaded'  , 'VTM Slider'  )
        #QgsMessageLog.logMessage( sql  , 'VTM Slider'  )

        #for i in self.propertiesTriggeringPostProcessing:
        #    cur.execute(sql, {'entity_id': i[0], 'property_type_id': i[1]})
        #    QgsMessageLog.logMessage( 'executing query with param :'+str(i[0])+';'+str(i[1]) , 'VTM Slider'  )
        #cur.close()

        #self.propertiesTriggeringPostProcessing = []