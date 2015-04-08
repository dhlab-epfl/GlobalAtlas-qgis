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
from PyQt4 import uic

from qgis.core import *
from qgis.gui import *

from VTMHelp import VTMHelp
from VTMLoadData import VTMLoadData
from VTMDebug import VTMDebug

from qgis.core import *

import os.path
import re

dateRange = [0,2050]

class VTMToolBar(QDockWidget):

    def __init__(self, iface, main):
        self.iface = iface
        self.main = main


        # postprocessing

        self.postProcEntitiesPropertiesIds = []


        # UI

        QDockWidget.__init__(self)
        uic.loadUi(os.path.dirname(__file__)+'/ui/vtmtoolbar.ui', self)

        self.helpButton.pressed.connect(self.doHelp)  
        self.debugButton.pressed.connect(self.doDebug)   
        self.openButton.pressed.connect(self.doOpenFile)   

        self.loadDataButton.pressed.connect(self.doLoadData)  

        self.refreshButton.pressed.connect(self.doRefresh)  

        self.mergeButton.pressed.connect(self.doMerge)
        self.explodeButton.pressed.connect(self.doExplode)

        self.notexistButton.pressed.connect(self.doNotexist)
        self.copytodateButton.pressed.connect(self.doCopytodate)
        self.cloneButton.pressed.connect(self.doClone)

        self.createrelationsButton.pressed.connect(self.doCreaterelations)
        self.removerelationsButton.pressed.connect(self.doRemoverelations)

        self.setBordersButton.pressed.connect(self.doSetBorders)
        self.selectBordersButton.pressed.connect(self.doSelectBorders)

        self.viewEntityButton.pressed.connect(self.doViewentity)
        self.listEventsButton.pressed.connect(self.doListproperties)

        self.slider.valueChanged.connect( self.spinboxYear.setValue )
        self.spinboxYear.valueChanged.connect( self.slider.setValue )

        self.slider.valueChanged.connect( self.doDate )
        self.spinboxYear.valueChanged.connect( self.doDate )

        self.minValueSpinBox.valueChanged.connect( self.slider.setMinimum )
        self.maxValueSpinBox.valueChanged.connect( self.slider.setMaximum )
        self.minValueSpinBox.valueChanged.connect( self.spinboxYear.setMinimum )
        self.maxValueSpinBox.valueChanged.connect( self.spinboxYear.setMaximum )



    def enablePlugin(self):
        self.activeWidget.setEnabled(True)
    
    def disablePlugin(self):
        self.activeWidget.setEnabled(False)


    ############################################################################################
    # GENERAL TOOLS   
    # File / Settings / Etc...                
    ############################################################################################

    def doOpenFile(self):
        path = os.path.join( os.path.dirname(__file__),'qgis','dataentry.qgs')
        self.iface.addProject( path )
        self.main.loadLayers()

    def doHelp(self):
        dlg = VTMHelp()
        dlg.exec_()

    def doDebug(self):
        dlg = VTMDebug(self.iface, self.main)
        dlg.exec_()

    def doLoadData(self):
        if self.iface.activeLayer() is None:
            self.iface.messageBar().pushMessage("VTM Slider","You must select vector a layer to load.", QgsMessageBar.WARNING, 2)
            return
        if self.iface.activeLayer().type() != QgsMapLayer.VectorLayer:
            self.iface.messageBar().pushMessage("VTM Slider","The selected layer is not a vector layer.", QgsMessageBar.WARNING, 2)
            return
        loadDataDialog = VTMLoadData(self.iface, self.main)
        loadDataDialog.exec_()
    

    ############################################################################################
    # SLIDER
    # Move in time                
    ############################################################################################
    
    def doDate(self, date):
        for layer in [self.main.eventsPointLayer, self.main.eventsLineLayer, self.main.eventsPolygonLayer]:
            layer.setSubsetString( re.sub('\/\*\*\/[0-9.]*\/\*\*\/','/**/'+str(date)+'/**/',self.main.sqlFilter) )

        self.iface.mapCanvas().refresh()


    ############################################################################################
    # BASIC        
    # Basic functions                
    ############################################################################################

    def doRefresh(self):
        """Performs the postprocessing of all selected properties' entities"""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # gbb_compute_geometries.sql
        for f in layer.selectedFeatures():
            self.main.runQuery('queries/gbb_compute_geometries', {'entity_id': f.attribute('entity_id')})

        # gbb_compute_geometries.sql
        for f in layer.selectedFeatures():
            self.main.runQuery('queries/clone_compute', {'entity_id': f.attribute('entity_id')})
        
        # basic_compute_dates.sql
        for f in layer.selectedFeatures():
            self.main.runQuery('queries/basic_compute_dates', {'entity_id': f.attribute('entity_id'), 'property_type_id': f.attribute('property_type_id')})
        self.main.commit()

    def doMerge(self):
        """Performs the merge of several properties into one entity

        It will assign the same entity_id to all properties, using the smallest entity_id of them all, and then postprocesses the entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )
        
        # basic_merge_features.sql        
        propertiesIds = layer.selectedFeaturesIds()
        entitiesIds = ( f.attribute('entity_id') for f in layer.selectedFeatures() )
        smallestEntityId = min(i for i in entitiesIds if i is not None) 

        self.main.runQuery('queries/basic_merge_features', {'entity_id': smallestEntityId, 'property_ids': propertiesIds})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();


        layer.removeSelection()

    def doExplode(self):
        """Performs the differentiation of several properties into different entities

        It will keep the entity_id of the property with the lower id, and assign entity_id to NULL to all properties, which will result on automatic creation of entities for those"""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return


        # postprocessing
        self.preparePostProcessingFromSelection( layer )
        
        # basic_unmerge_feature.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/basic_unmerge_features', {'property_ids': propertiesIds})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()

    def doNotexist(self):
        """Sets the value to NULL at the current date for the current entites / properties"""       

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )
        
        # basic_does_not_exist.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/basic_does_not_exist', {'property_ids': propertiesIds, 'date':self.spinboxYear.value()})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()

    def doCopytodate(self):
        """Creates a copy of the property at the current date"""       

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )

        # basic_duplicate_to_date.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/basic_duplicate_to_date', {'property_ids': propertiesIds, 'date':self.spinboxYear.value()})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()

    
    ############################################################################################
    # CLONE
    # Clone functions                
    ############################################################################################
    
    def doClone(self):
        """Creates a clone of the property at the current date"""       

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )

        # basic_duplicate_to_date.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/clone_insert', {'properties_ids': propertiesIds, 'date':self.spinboxYear.value()})
        self.main.commit()

        # gbb_compute_geometries.sql
        for f in layer.selectedFeatures():
            self.main.runQuery('queries/clone_compute', {'entity_id': f.attribute('entity_id')})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()

    ############################################################################################
    # VIEW
    # Display functions                
    ############################################################################################

    def doListproperties(self):
        """Selects properties corresponding to current entitiy_ids from the unfiltered properties table and show it"""

        self.main.eventsLayer.removeSelection()

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        entitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        
        filterExpr = '"entity_id" IN ({0})'.format( ','.join( (str(i) for i in entitiesIds) ) )
        properties = self.main.eventsLayer.getFeatures( QgsFeatureRequest().setFilterExpression( filterExpr ) )
        
        self.main.eventsLayer.setSelectedFeatures( [f.id() for f in properties] )

        self.iface.showAttributeTable(self.main.eventsLayer)

    def doViewentity(self):
        """Selects the entities corresponding to the current selected properties"""

        self.main.entitiesLayer.removeSelection()

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        entitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)

        self.main.entitiesLayer.setSelectedFeatures( entitiesIds )
        self.iface.showAttributeTable(self.main.entitiesLayer)
        

    ############################################################################################
    # RELATIONS
    # Tools to create / edit succession relations                
    ############################################################################################
   
    def doCreaterelations(self):
        """Creates relations between all selected entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )

        # create_relations.sql        
        propertiesIds = list(set(layer.selectedFeaturesIds()))
        entitiesIds = [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

        self.main.runQuery('queries/succ_insert_successions', {'entities_ids': entitiesIds})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()

    def doRemoverelations(self):
        """Remove relations between all selected entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing
        self.preparePostProcessingFromSelection( layer )

        # create_relations.sql        
        propertiesIds = list(set(layer.selectedFeaturesIds()))
        entitiesIds = [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

        self.main.runQuery('queries/succ_remove_successions', {'entities_ids': entitiesIds})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();


        layer.removeSelection()


    ############################################################################################
    # BORDERS
    # Tools to create / edit borders relations                
    ############################################################################################

    def doSelectBorders(self):
        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        entitiesIds = [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

        self.main.eventsPolygonLayer.removeSelection()
        self.main.eventsLineLayer.removeSelection()
        self.main.eventsPointLayer.removeSelection()

        result = self.main.runQuery('queries/gbb_select_borders_for_entities', {'entities_ids': entitiesIds })

        self.main.eventsLineLayer.setSelectedFeatures( [i[0] for i in result.fetchall()] )

    def doSetBorders(self):
        entitiesIds = list(set([ f.attribute('entity_id') for f in (self.main.eventsPolygonLayer.selectedFeatures()+self.main.eventsPointLayer.selectedFeatures()) ])) # note : if these throw bugs, it's because there is a selection of a feature that disapareed (so selectedFateures is an array of disappared features, that have no attributes)
        borderIds = list(set( [f.attribute('entity_id') for f in self.main.eventsLineLayer.selectedFeatures()] ))

        if len(borderIds) == 0:
            self.iface.messageBar().pushMessage("VTM Slider","You need to selected at least one linestring to act as a border.", QgsMessageBar.WARNING, 2)
            return 

        # If no entity was set, we create one
        if len(entitiesIds) == 0:            
            result = self.main.runQuery('queries/basic_insert_blank')
            entitiesIds = [result.fetchone()['id']];

        # postprocessing
        self.preparePostProcessing( [[entityId,1] for entityId in entitiesIds ] );

        for entityId in entitiesIds:
            self.main.runQuery('queries/gbb_insert_relation', {'entity_id': entityId, 'borders_ids': borderIds})
            self.main.runQuery('queries/gbb_compute_geometries', {'entity_id': entityId})
            self.main.runQuery('queries/basic_compute_dates', {'entity_id': entityId, 'property_type_id': 1})
        self.main.commit()

        # postprocessing
        self.commitPostProcessing();

        self.main.eventsPolygonLayer.removeSelection()
        self.main.eventsLineLayer.removeSelection()
        self.main.eventsPointLayer.removeSelection()
        


    ############################################################################################
    # POSTPROCESSING
    # Helpers to trigger postprocessing                
    ############################################################################################

    def preparePostProcessingFromSelection(self, layer):
        """Sets the array of [entities,property_type] that will have to be postprocessed from the current selection"""
        # for basic_compute_dates.sql
        self.preparePostProcessing( [ [f.attribute('entity_id'),f.attribute('property_type_id')] for f in layer.selectedFeatures() ] )
    def preparePostProcessing(self, entitiesPropertiesIds):
        """Sets the array of [entities,property_type] that will have to be postprocessed"""
        # for basic_compute_dates.sql
        self.postProcEntitiesPropertiesIds += entitiesPropertiesIds

    def commitPostProcessing(self):
        # basic_compute_dates.sql
        for entityId, propertyTypeId in self.postProcEntitiesPropertiesIds:
            self.main.runQuery('queries/basic_compute_dates', {'entity_id': entityId, 'property_type_id': propertyTypeId})
        self.main.commit()
        self.postProcEntitiesPropertiesIds = []
        self.iface.mapCanvas().refresh()


    ############################################################################################
    # HELPERS
    # Helpers to get current layer                
    ############################################################################################

    def _getLayerIfEventsLayersAndSelection(self):
        """Return the active layer if it's one of the events layers, or returns None with a message if it's not"""
        layer = self.iface.activeLayer()
        if layer not in [self.main.eventsPointLayer, self.main.eventsLineLayer, self.main.eventsPolygonLayer, self.main.eventsLayer]:
            self.iface.messageBar().pushMessage("VTM Slider","You must use this function on one of the properties layer.", QgsMessageBar.WARNING, 2)
            return None
        if len(layer.selectedFeaturesIds())==0:
            self.iface.messageBar().pushMessage("VTM Slider","You need a selection to run this function.", QgsMessageBar.WARNING, 2)
            return None
        return layer


