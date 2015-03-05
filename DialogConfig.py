# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from qgis.core import *

import os.path

class DialogConfig(QDialog):

    def __init__(self, iface):

        self.iface = iface

        self.filterString = ""
        self.eventsLayer = ""
        self.entitiesLayer = ""
        self.relationsLayer = ""
        self.timelayers = []

        QDialog.__init__(self)

        uic.loadUi(os.path.dirname(__file__)+'/ui/config.ui', self)

        self.accepted.connect(self.saveDefaults)


    def showEvent(self, event):
        QDialog.showEvent(self, event)
        self.refreshWidgets()


    def refreshWidgets(self):
        self.timelayersComboBox.clear()
        self.eventsLayerComboBox.clear()
        self.entitiesLayerComboBox.clear()
        self.relationsLayerComboBox.clear()
        for l in self.iface.legendInterface().layers():
            if l.type() == QgsMapLayer.VectorLayer:
                self.timelayersComboBox.addItem( l.name(), l.id() )
                self.eventsLayerComboBox.addItem( l.name(), l.id() )
                self.entitiesLayerComboBox.addItem( l.name(), l.id() )
                self.relationsLayerComboBox.addItem( l.name(), l.id() )

        self.timelayersAddButton.pressed.connect( self.doAddLayer )
        self.timelayersRemoveButton.pressed.connect( self.doRemoveLayer )

        self.loadDefaults()

    def doAddLayer(self):
        self.timelayersList.addItem( self.timelayersComboBox.itemData( self.timelayersComboBox.currentIndex() ) )
    def doRemoveLayer(self):
        self.timelayersList.takeItem(self.timelayersList.currentRow())

    def saveDefaults(self):
        self.updateValuesFromWidgets()
        # store values
        proj = QgsProject.instance()
        proj.writeEntry("VTMSlider", "filterString", self.filterString )
        proj.writeEntry("VTMSlider", "timelayers", self.timelayers)
        proj.writeEntry("VTMSlider", "eventsLayer", self.eventsLayer)
        proj.writeEntry("VTMSlider", "entitiesLayer", self.entitiesLayer)
        proj.writeEntry("VTMSlider", "relationsLayer", self.relationsLayer)

    def loadDefaults(self):
        # read values
        proj = QgsProject.instance()
        self.filterString = proj.readEntry("VTMSlider", "filterString", None)[0]
        self.eventsLayer = proj.readEntry("VTMSlider", "eventsLayer", None)[0]
        self.entitiesLayer =  proj.readEntry("VTMSlider", "entitiesLayer", None)[0]
        self.relationsLayer =  proj.readEntry("VTMSlider", "relationsLayer", None)[0]
        self.timelayers = proj.readListEntry("VTMSlider", "timelayers", [])[0]

        self.updateWidgetsFromValues()

    def updateValuesFromWidgets(self):
        self.filterString = self.filterTextEdit.toPlainText()
        self.eventsLayer = self.eventsLayerComboBox.itemData( self.eventsLayerComboBox.currentIndex() )
        self.entitiesLayer = self.entitiesLayerComboBox.itemData( self.entitiesLayerComboBox.currentIndex() )
        self.relationsLayer = self.relationsLayerComboBox.itemData( self.relationsLayerComboBox.currentIndex() )
        self.timelayers = []
        for row in range(0, self.timelayersList.count() ):
            self.timelayers.append( self.timelayersList.item( row ).text() )

    def updateWidgetsFromValues(self):
        self.filterTextEdit.setPlainText( self.filterString )
        self.eventsLayerComboBox.setCurrentIndex( self.eventsLayerComboBox.findData( self.eventsLayer ) )
        self.entitiesLayerComboBox.setCurrentIndex( self.entitiesLayerComboBox.findData( self.entitiesLayer ) )
        self.relationsLayerComboBox.setCurrentIndex( self.relationsLayerComboBox.findData( self.relationsLayer ) )
        self.timelayersList.clear()
        for lay in self.timelayers:
            self.timelayersList.addItem( lay )






