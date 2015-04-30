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

from qgis.core import *
from qgis.gui import *

class VTMTool():

    currentTool = None

    @staticmethod
    def activate(toolclass, iface, main, button):
        if VTMTool.currentTool is None:
            VTMTool.currentTool = toolclass(iface, main, button)
        elif VTMTool.currentTool.__class__ != toolclass:
            VTMTool.currentTool.terminate()
            VTMTool.currentTool = toolclass(iface, main, button)
        VTMTool.currentTool.doTrigger()




    def __init__(self, iface, main, button):
        VTMTool.currentTool = self

        self.iface = iface
        self.main = main
        self.button = button

        self.postProcEntitiesPropertiesIds = []

        self.button.setCheckable(True)
        self.button.setChecked(False)   
        self.doInit()

    def terminate(self):
        self.button.setCheckable(False)
        self.button.setChecked(False)
        self.doTerminate()

    def doInit(self):
        QgsMessageLog.logMessage('{} does not implement doInit'.format(self.__class__.__name__))
    def doTrigger(self):
        QgsMessageLog.logMessage('{} does not implement doTrigger'.format(self.__class__.__name__))
    def doTerminate(self):
        QgsMessageLog.logMessage('{} does not implement doTerminate'.format(self.__class__.__name__))


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

    def _getSelectedEntitiesIds(self):
        layer = self._getLayerIfEventsLayersAndSelection()
        return [ f.attribute('entity_id') for f in layer.selectedFeatures() ]

    def _getSelectedPropertiesIds(self):
        layer = self._getLayerIfEventsLayersAndSelection()
        return layer.selectedFeaturesIds()

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

    def check(self):
        self.button.setCheckable(True)
        self.button.setChecked(True)
    def uncheck(self):
        self.button.setCheckable(False)
        self.button.setChecked(False)


class VTMMergeTool(VTMTool):

    def doInit(self):
        self.baseEntityId = None

    def doTrigger(self):
        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        entitiesIds = self._getSelectedEntitiesIds()

        if self.baseEntityId is None and len(entitiesIds) == 1:
            self.baseEntityId = entitiesIds[0]

            self.check()
            self.iface.messageBar().pushMessage("VTM Slider","Base entity id registerd. Now select other properties to merge into this.", QgsMessageBar.INFO, 2)
            layer.removeSelection()
        else:

            if self.baseEntityId is None:
                self.baseEntityId = min(i for i in entitiesIds if i is not None) 

            # postprocessing
            self.preparePostProcessingFromSelection( layer )

            # basic_merge_features.sql   
            self.main.runQuery('queries/basic_merge_features', {'entity_id': self.baseEntityId, 'property_ids': self._getSelectedPropertiesIds() })
            self.main.commit()

            # postprocessing
            self.commitPostProcessing();
            
            self.uncheck()
            self.iface.messageBar().pushMessage("VTM Slider","Merge done.", QgsMessageBar.INFO, 2)
            layer.removeSelection()
            self.terminate()


    def doTerminate(self):
        self.baseEntityId = None


class VTMExplodeTool(VTMTool):

    def doTrigger(self):
        """Performs the differentiation of several properties into different entities

        It will keep the entity_id of the property with the lower id, and assign entity_id to NULL to all properties, which will result on automatic creation of entities for those"""

        layer = self._getLayerIfEventsLayersAndSelection()
        if layer is None: return

        # postprocessing of selected properties
        self.preparePostProcessingFromSelection( layer )
        
        # basic_unmerge_feature.sql
        propertiesIds = layer.selectedFeaturesIds()

        resulting_entity_ids = self.main.runQuery('queries/basic_unmerge_features', {'property_ids': propertiesIds})
        self.main.commit()
        
        # postprocessing of affected entities
        for rec in resulting_entity_ids:
            self.preparePostProcessing( [[rec['entity_id'], rec['property_type_id']]] )

        # postprocessing
        self.commitPostProcessing();

        layer.removeSelection()




