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

        self.createrelationsButton.pressed.connect(self.doCreaterelations)
        self.removerelationsButton.pressed.connect(self.doRemoverelations)

        self.viewEntityButton.pressed.connect(self.doViewentity)
        self.listEventsButton.pressed.connect(self.doListproperties)
        self.viewRelationsButton.pressed.connect(self.doViewrelations)

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



    def doOpenFile(self):
        path = os.path.join( os.path.dirname(__file__),'qgis','dataentry.qgs')
        self.iface.addProject( path )
        self.main.loadLayers()

    def doDate(self, date):

        for layer in [self.main.eventsPointLayer, self.main.eventsLineLayer, self.main.eventsPolygonLayer]:
            layer.setSubsetString( re.sub('\/\*\*\/[0-9.]*\/\*\*\/','/**/'+str(date)+'/**/',self.main.sqlFilter) )

        self.iface.mapCanvas().refresh()

    def doHelp(self):
        dlg = VTMHelp()
        dlg.exec_()

    def doDebug(self):
        dlg = VTMDebug(self.iface, self.main)
        dlg.exec_()

    def doLoadData(self):
        loadDataDialog = VTMLoadData(self.iface, self.main)
        loadDataDialog.exec_()
    
    def doRefresh(self):
        """Performs the postprocessing of all selected properties' entities"""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # compute_dates.sql
        for f in layer.selectedFeatures():
            self.main.runQuery('queries/compute_dates', {'entity_id': f.attribute('entity_id'), 'property_type_id': f.attribute('property_type_id')})
        self.main.commit()


    def doMerge(self):
        """Performs the merge of several properties into one entity

        It will assign the same entity_id to all properties, using the smallest entity_id of them all, and then postprocesses the entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)

        # merge_feature.sql        
        propertiesIds = layer.selectedFeaturesIds()
        entitiesIds = ( f.attribute('entity_id') for f in layer.selectedFeatures() )
        smallestEntityId = min(i for i in entitiesIds if i is not None) 

        self.main.runQuery('queries/merge_features', {'entity_id': smallestEntityId, 'property_ids': propertiesIds})
        self.main.commit()

        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()


        layer.removeSelection()

    def doExplode(self):
        """Performs the differentiation of several properties into different entities

        It will keep the entity_id of the property with the lower id, and assign entity_id to NULL to all properties, which will result on automatic creation of entities for those"""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # for compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)

        # unmerge_feature.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/unmerge_features', {'property_ids': propertiesIds})
        self.main.commit()

        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()

        layer.removeSelection()


    def doNotexist(self):
        """Sets the value to NULL at the current date for the current entites / properties"""       

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # for compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)


        # does_not_exist.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/does_not_exist', {'property_ids': propertiesIds, 'date':self.spinboxYear.value()})
        self.main.commit()


        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()

        layer.removeSelection()

    def doListproperties(self):
        """Selects properties corresponding to current entitiy_ids from the unfiltered properties table and show it"""

        self.main.eventsLayer.removeSelection()

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        entitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        
        filterExpr = '"entity_id" IN ({0})'.format( ','.join( (str(i) for i in entitiesIds) ) )
        properties = self.main.eventsLayer.getFeatures( QgsFeatureRequest().setFilterExpression( filterExpr ) )
        
        self.main.eventsLayer.setSelectedFeatures( [f.id() for f in properties] )

        self.iface.showAttributeTable(self.main.eventsLayer)

    def doViewentity(self):
        """Selects the entities corresponding to the current selected properties"""

        self.main.entitiesLayer.removeSelection()

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        entitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)

        self.main.entitiesLayer.setSelectedFeatures( entitiesIds )
        self.iface.showAttributeTable(self.main.entitiesLayer)

        return

    def doViewrelations(self):
        """Selects the relations corresponding to the current selected properties"""

        self.main.relationsLayer.removeSelection()

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        entitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        
        filterExpr = '"a_id" IN ({0}) OR "b_id" IN ({0})'.format( ','.join( (str(i) for i in entitiesIds) ) )
        relationsIds = [f.id() for f in self.main.relationsLayer.getFeatures( QgsFeatureRequest().setFilterExpression( filterExpr ) )]

        if len(relationsIds)==0:
            self.iface.messageBar().pushMessage("VTM Slider","There is no relation for these entities", QgsMessageBar.INFO, 2)
            return
        
        self.main.relationsLayer.setSelectedFeatures( relationsIds )
        self.iface.showAttributeTable(self.main.relationsLayer)
        

    def doCopytodate(self):
        """Creates a copy of the property at the current date"""       

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # for compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)


        # copy_to_date.sql
        propertiesIds = layer.selectedFeaturesIds()

        self.main.runQuery('queries/copy_to_date', {'property_ids': propertiesIds, 'date':self.spinboxYear.value()})
        self.main.commit()


        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()

        layer.removeSelection()


    def doCreaterelations(self):
        """Creates relations between all selected entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)

        # create_relations.sql        
        propertiesIds = list(set(layer.selectedFeaturesIds()))
        entitiesIds = [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

        self.main.runQuery('queries/create_relations', {'entities_ids': entitiesIds})
        self.main.commit()

        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()


        layer.removeSelection()

    def doRemoverelations(self):
        """Remove relations between all selected entities."""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None:
            return

        # compute_dates.sql
        postProcEntitiesIds = list(set( f.attribute('entity_id') for f in layer.selectedFeatures() )) # these are the ids of all entities (needed for postprocessing)
        postProcPropertyTypeIds = list(set( f.attribute('property_type_id') for f in layer.selectedFeatures() )) # these are the ids of all properties types (needed for postprocessing)

        # create_relations.sql        
        propertiesIds = list(set(layer.selectedFeaturesIds()))
        entitiesIds = [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

        self.main.runQuery('queries/remove_relations', {'entities_ids': entitiesIds})
        self.main.commit()

        # compute_dates.sql
        for entityId in postProcEntitiesIds:
            self.main.runQuery('queries/compute_dates', {'entity_id': entityId, 'property_type_ids': postProcPropertyTypeIds})
        self.main.commit()


        layer.removeSelection()

        return




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


