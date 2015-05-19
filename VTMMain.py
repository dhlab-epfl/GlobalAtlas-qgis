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
import psycopg2.extras

import os.path


class VTMMain:
    """Main class

    Handles things such as postgis connection, layer loading, layer edit events"""


    instance = None

    sqlFilter = '("computed_date_start" IS NULL OR "computed_date_start"<=/**/2015/**/) AND ("computed_date_end" IS NULL OR "computed_date_end">/**/2015/**/)'
    eventsPointLayerID = 'properties_for_qgis20150317102814809'
    eventsLineLayerID = 'properties_for_qgis20150307041406392'
    eventsPolygonLayerID = 'properties_for_qgis20150307001918975'
    eventsLayerID = 'properties20150212181047441'
    entitiesLayerID = 'entities20150212181047504'
    entitiesTypeLayerID = 'entity_types20150306220740482'
    propertiesTypeLayerID = 'properties_types20150317175434094'
    sourcesLayerID = 'sources20150212181047520'

    eventsPointLayer = None
    eventsLineLayer = None
    eventsPolygonLayer = None
    eventsLayer = None
    entitiesLayer = None
    propertiesTypeLayer = None
    entitiesTypeLayer = None
    sourcesLayer = None

    uri = None

    def __init__(self, iface):
        self.plugin_dir = os.path.dirname(__file__)
        
        # Save reference to the QGIS interface
        self.iface = iface
        VTMMain.instance = self

        self.connection = None
        self.sqlQueries = {}

        self.setDatabase( QSettings().value("VTM Slider/database", "vtm_dev") )
        

    def initGui(self):
        """ Put your code here and remove the pass statement"""

        self.dockwidget = VTMToolBar(self.iface, self)
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea,self.dockwidget)
        self.dockwidget.show()

        self.iface.newProjectCreated.connect( self.loadLayers )

        self.loadLayers()

    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockwidget)
        self.iface.newProjectCreated.disconnect( self.loadLayers )

    def setDatabase(self, db):
        database = db
        username = QSettings().value("VTM Slider/username", "")
        password = QSettings().value("VTM Slider/password", "")
        QgsMessageLog.logMessage('WARNING : password stored in plain text in the registry for debugging purposes !', 'VTM Slider')
        self.uri = 'dbname=\'{db}\' host=dhlabpc3.epfl.ch port=5432 sslmode=disable'.format(db=database)
        QgsCredentials.instance().put(self.uri, username, password)
        QgsMessageLog.logMessage('setting credentials: '+self.uri+' '+username+'//'+password, 'VTM Slider')

        QSettings().setValue("VTM Slider/database", database)

    def currentDate(self):
        return self.dockwidget.slider.value()


    

    def loadLayers(self):

        ############################################################
        # Get and check the SQL connection
        ############################################################

        self.connection = self.getConnection()
        if self.connection is None:           
            QgsMessageLog.logMessage('Unable to establish connection. Plugin will not work. Make sure you opened the provided QGIS project and entered the correct credentials.','VTM Slider')
            self.dockwidget.disablePlugin()
            return

        QgsMessageLog.logMessage('Connection successful.','VTM Slider')

        ############################################################
        # Get the references to the layers using their IDs
        ############################################################

        self.eventsPointLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsPointLayerID)
        self.eventsLineLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsLineLayerID)
        self.eventsPolygonLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsPolygonLayerID)
        self.eventsLayer = QgsMapLayerRegistry.instance().mapLayer(self.eventsLayerID)
        self.entitiesLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesLayerID)
        self.propertiesTypeLayer = QgsMapLayerRegistry.instance().mapLayer(self.propertiesTypeLayerID)
        self.entitiesTypeLayer = QgsMapLayerRegistry.instance().mapLayer(self.entitiesTypeLayerID)
        self.sourcesLayer = QgsMapLayerRegistry.instance().mapLayer(self.sourcesLayerID)

        if self.eventsPointLayer is None or self.eventsLineLayer is None or self.eventsPolygonLayer is None or self.eventsLayer is None or self.entitiesLayer is None or self.propertiesTypeLayer is None or self.entitiesTypeLayer is None:
            QgsMessageLog.logMessage('Unable to load some needed VTM layers. Plugin will not work. Make sure you opened the provided QGIS project.','VTM Slider')
            self.dockwidget.disablePlugin()
            return

        QgsMessageLog.logMessage('Loaded all needed layers.','VTM Slider')


        ############################################################
        # If everything worked, connect the signals to make the post processing queries
        ############################################################
        self.connectSignalsForPostProcessing()


        self.dockwidget.enablePlugin()
        QgsMessageLog.logMessage('Plugin will work.','VTM Slider')


    ############################################################################################
    #
    # SIGNALS FOR POSTPROCESSING         
    #                  
    # These signals connect the slots for postprocessin (see below) on all events layers
    #                
    ############################################################################################

    def connectSignalsForPostProcessing(self):
        self.entityIdsToPostprocess = [] # this will store ids to postprocess after commit, we need it because we can only get the deleted entity ids before commit


        # Signals for insert of events
        for layer in [self.eventsPointLayer, self.eventsLineLayer, self.eventsPolygonLayer, self.eventsLayer]:
            layer.committedFeaturesAdded.connect( self.committedFeaturesAdded )
            layer.committedAttributeValuesChanges.connect( self.committedAttributeValuesChanges )
            layer.committedGeometriesChanges.connect( self.committedGeometriesChanges )
            layer.featureDeleted.connect( lambda pid: self.featureDeleted(layer, pid) )
            layer.editingStopped.connect( self.editingStopped )


    ############################################################################################
    #
    # SLOTS FOR POSTPROCESSING         
    #                  
    # Those slots are triggered when features were added / modified / deleted
    # and allow to store the list of entities/properties_types that must be
    # postprocessed in self.entityIdsToPostprocess
    #                
    ############################################################################################

    def committedFeaturesAdded(self, layerID, addedFeatures):
        layer = QgsMapLayerRegistry.instance().mapLayer(layerID)
        eidx = layer.fieldNameIndex('entity_id') # workaround (see below)
        ptidx = layer.fieldNameIndex('property_type_id') # workaround (see below)
        for feat in addedFeatures:
            #eid = feat.attribute('entity_id') # bug for some reason this doesnt work on non geometric layers
            #ptid = feat.attribute('property_type_id') # bug for some reason this doesnt work on non geometric layers
            eid = feat.attributes()[eidx] # workaround
            ptid = feat.attributes()[ptidx] # workaround
            self.entityIdsToPostprocess.append( [eid, ptid] )
        
    def committedAttributeValuesChanges(self, layerID, changedAttributesValues):
        QgsMessageLog.logMessage( 'committedAttributeValuesChanges '+str(changedAttributesValues) , 'VTM Slider'  )
        layer = QgsMapLayerRegistry.instance().mapLayer(layerID)
        eidx = layer.fieldNameIndex('entity_id') # workaround (see below)
        ptidx = layer.fieldNameIndex('property_type_id') # workaround (see below)
        for fid in changedAttributesValues:

            features = layer.getFeatures( QgsFeatureRequest( fid ) )
            for f in features: # We're supposed to have only one feature here
                #eid = feat.attribute('entity_id') # bug for some reason this doesnt work on non geometric layers
                #ptid = feat.attribute('property_type_id') # bug for some reason this doesnt work on non geometric layers
                eid = f.attributes()[eidx] # workaround
                ptid = f.attributes()[ptidx] # workaround
                self.entityIdsToPostprocess.append( [eid,ptid] )

    def committedGeometriesChanges(self, layerID, changedGeometriesValues):
        QgsMessageLog.logMessage( 'committedGeometriesChanges '+str(changedGeometriesValues) , 'VTM Slider'  )
        layer = QgsMapLayerRegistry.instance().mapLayer(layerID)
        eidx = layer.fieldNameIndex('entity_id') # workaround (see below)
        ptidx = layer.fieldNameIndex('property_type_id') # workaround (see below)
        for fid in changedGeometriesValues:

            features = layer.getFeatures( QgsFeatureRequest( fid ) )
            for f in features: # We're supposed to have only one feature here
                #eid = feat.attribute('entity_id') # bug for some reason this doesnt work on non geometric layers
                #ptid = feat.attribute('property_type_id') # bug for some reason this doesnt work on non geometric layers
                eid = f.attributes()[eidx] # workaround
                ptid = 1 # workaround
                self.entityIdsToPostprocess.append( [eid,ptid] )

    def featureDeleted(self, layer, pid): 
        """This is triggered when a feature is deleted in QGIS, in the vector layer buffer

        We need to get this at this moment (before the deletion is commited), because we need to get
        the entity_id and property_type_id to run the postprocessing after the commit is made."""

        # Features with negative ids have not yet been commited to the database, so there's nothing to do
        if pid<0:
            return

        result = self.runQuery('queries/select_entity_and_property_type', {'pid': pid})
        rec = result.fetchone()
        self.entityIdsToPostprocess.append( [rec['entity_id'], rec['property_type_id'] ] )
        
    def editingStopped(self):
        """Post processing after insert/edit/updates in on of the eventsLayers"""

        QgsMessageLog.logMessage("Postprocessing "+str(self.entityIdsToPostprocess),"VTM Slider")

        # Some entityIds are QPyNullVariant if the entity was not created yet. In this case, we need no postprocesing anyways.
        existingEntityIdsToPostprocess = [[entityId, propTypeId] for entityId, propTypeId in self.entityIdsToPostprocess if entityId]
        
        # gbb_compute_geometries.sql
        for entityId, propTypeId in existingEntityIdsToPostprocess:
            self.runQuery('queries/clone_compute', {'entity_id': entityId}) #TODO : do it for property only
        self.commit()

        # compute_geometries_from_borders.sql
        result = self.runQuery('queries/gbb_get_entities_to_postprocess', {'modified_entities_ids': [entityId for entityId, propTypeId in existingEntityIdsToPostprocess]})
        for rec in result:
            eid = rec['entity_id']
            self.runQuery('queries/gbb_compute_geometries', {'entity_id': eid})
            existingEntityIdsToPostprocess.append ( [eid, 1] ) # Those dates must be computed too
        self.commit()

        # basic_compute_dates.sql
        for entityId, propTypeId in existingEntityIdsToPostprocess:
            if not propTypeId: #this could be QPyNullVariant if no property was specified, in which case we have the geom (1) proeprty type
                propTypeId = 1
            self.runQuery('queries/basic_compute_dates', {'entity_id': entityId, 'property_type_id': propTypeId})
        self.commit()



        self.entityIdsToPostprocess = []


    ############################################################################################
    #
    # CONNEXTION TO THE DATABASE         
    #                  
    # These functions manage the connection and the queries to the database
    #                
    ############################################################################################

    def getConnection(self):

        ############################################################
        # Get the postgres connection using the eventsLayer uri and credentials
        ############################################################

        connection = None
        
        dsUri = QgsDataSourceURI( self.uri )
        connectionInfo = dsUri.connectionInfo()
        
        host = dsUri.host()
        port = int(dsUri.port())
        database = dsUri.database()
        username = None
        password = None


        # We try to get the credentials
        (ok, username, password) = QgsCredentials.instance().get(connectionInfo.encode('utf-8'), username, password)

        if not ok:
            QgsMessageLog.logMessage('Could not get the credentials. Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings.','VTM Slider')
            return None
        try:
            # We try now to connect using those credentials (host, port, database, username, password )
            connection = psycopg2.connect( host=host, port=port, database=database, user=username, password=password )
            QgsCredentials.instance().put(connectionInfo, username, password)
            QSettings().setValue("VTM Slider/username", username)
            QSettings().setValue("VTM Slider/password", password) # TODO : REMOVE THIS !!!!! IT STORES THE PASSWORD IN PLAIN TEXT IN THE REGISTRY !!!
        except Exception as e:
            QgsMessageLog.logMessage('Could not connect with provided credentials. Plugin will not work. Make sure you opened the provided QGIS project and entered the correction postgis connection settings. Error was {0}'.format( str(e) ),'VTM Slider')
            return None            

        return connection

    def runQuery(self, filename, parameters={}):
        QgsMessageLog.logMessage('Running query {0} with parameters {1}'.format(filename, str(parameters)), 'VTM Slider')

        if not hasattr(self.sqlQueries,filename):
            self.sqlQueries[filename] = open( os.path.join( self.plugin_dir,'sql',filename+'.sql') ).read()

        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute( self.sqlQueries[filename], parameters )
        return cursor
        
    def commit(self):
        self.connection.commit()



