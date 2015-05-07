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

import os.path


class VTMLoadData(QDialog):

    PROPERTY_COLUMN = 0
    DATE_COLUMN = 1
    INTERP_COLUMN = 2
    VALUE_COLUMN = 3

    def __init__(self, iface, main):

        self.iface = iface
        self.main = main

        QDialog.__init__(self)
        uic.loadUi(os.path.dirname(__file__)+'/ui/loaddata.ui', self)


        self.layer = self.iface.activeLayer()
        crs = self.iface.activeLayer().crs().authid()



        # Update the GUI fields


        self.layerNameLabel.setText( self.layer.name() )

        self.entityNameLineEdit.setText( '\'{layername} #\' || $id'.format(layername=self.layer.name()) )

        for f in self.main.entitiesTypeLayer.getFeatures():
	        self.entityTypeComboBox.addItem( f.attribute('name'), f.id() )

        for f in self.main.propertiesTypeLayer.getFeatures():
	        self.addAttributeTypeComboBox.addItem( f.attribute('name'), f.id() )

        if self.layer.hasGeometryType():
            propItem = QTableWidgetItem('geom')
            dateItem = QTableWidgetItem( '2015' )
            interpItem = QTableWidgetItem( '\'default\'' )
            valItem = QTableWidgetItem('geomToWKT( transform($geometry,\'{0}\',\'EPSG:4326\') )'.format(crs))

            self.attributesTableWidget.insertRow(0)
            self.attributesTableWidget.setItem(0,self.PROPERTY_COLUMN,propItem)
            self.attributesTableWidget.setItem(0,self.DATE_COLUMN,dateItem)
            self.attributesTableWidget.setItem(0,self.INTERP_COLUMN,interpItem)
            self.attributesTableWidget.setItem(0,self.VALUE_COLUMN,valItem)


        if self.layer.selectedFeatureCount():
            self.selectionOnlyCheckBox.setCheckState(Qt.Checked)
        self.updateFeatureCountLabel()


        # Connect the signals

        self.attributesTableWidget.currentCellChanged.connect(self.currentCellChanged)

        self.entityExpressionButton.pressed.connect(self.buildEntityExpression)
        self.attributeExpressionButton.pressed.connect(self.buildAttributeExpression)

        self.addAttributeButton.pressed.connect(self.addProperty)
        self.removeAttributeButton.pressed.connect(self.removeProperty)

        self.accepted.connect( self.process )

        self.selectionOnlyCheckBox.stateChanged.connect( self.updateFeatureCountLabel )


    def buildEntityExpression(self):
        dialog = QgsExpressionBuilderDialog(self.layer, self.entityNameLineEdit.text())
        if dialog.exec_():
            self.entityNameLineEdit.setText( dialog.expressionText() )

    def buildAttributeExpression(self):
        dialog = QgsExpressionBuilderDialog(self.layer, self.attributesTableWidget.currentItem().text())
        if dialog.exec_():
            self.attributesTableWidget.currentItem().setText( dialog.expressionText() )

    def addProperty(self):
        propItem = QTableWidgetItem( self.addAttributeTypeComboBox.currentText() )
        dateItem = QTableWidgetItem( '2015' )
        interpItem = QTableWidgetItem( '\'default\'' )
        valItem = QTableWidgetItem( 'value' )

        self.attributesTableWidget.insertRow(self.attributesTableWidget.rowCount())

        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.PROPERTY_COLUMN,propItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.DATE_COLUMN,dateItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.INTERP_COLUMN,interpItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.VALUE_COLUMN,valItem)

    def removeProperty(self):
        self.attributesTableWidget.removeRow( self.addAttributeTypeComboBox.currentIndex() )

    def currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentColumn==self.DATE_COLUMN or currentColumn==self.INTERP_COLUMN  or currentColumn==self.VALUE_COLUMN:
            self.attributeExpressionButton.setEnabled(True)
        else:
            self.attributeExpressionButton.setEnabled(False)


    def updateFeatureCountLabel(self):
        count = 0
        if self.selectionOnlyCheckBox.isChecked():
            count = self.layer.selectedFeatureCount()
        else:
            count = self.layer.featureCount()

        self.featureCountLabel.setText( 'You are going to load {0} features'.format( count ) )

    def validateExpressions(self):
        pass

    def process(self):        
        # Here we do the actual loading

        featureIterator = None
        if self.selectionOnlyCheckBox.isChecked():
            featureIterator = self.layer.selectedFeaturesIterator()
        else:
            featureIterator = self.layer.getFeatures()

        connection = self.main.getConnection()
        cursor = connection.cursor()

        entityFields = self.main.entitiesLayer.pendingFields()

        for f in featureIterator:
            QgsMessageLog.logMessage( 'importing feature {0}'.format( f.id() ),'VTM Slider' )
            
            # 1. Creation of the entity

            expName = QgsExpression( self.entityNameLineEdit.text() )
            expName.prepare( entityFields )
            name = expName.evaluate( f )

            type_id = self.entityTypeComboBox.itemData( self.entityTypeComboBox.currentIndex() )

            sql = 'INSERT INTO vtm.entities(name, type_id) VALUES( %(name)s, %(type_id)s ) RETURNING id;'
            cursor.execute(sql, {'name': name , 'type_id': type_id})
            ent_id = cursor.fetchone()[0]

            QgsMessageLog.logMessage( 'tried to insert : '+str(name)+', '+str(type_id), 'VTM Slider')
            QgsMessageLog.logMessage( 'id created : '+str(ent_id), 'VTM Slider')


            # 2. Creation of the properties

            for row in range(0, self.attributesTableWidget.rowCount()):

                valueExpVal = QgsExpression( self.attributesTableWidget.item(row, self.VALUE_COLUMN).text() )
                valueExpVal.prepare( entityFields )
                val = valueExpVal.evaluate( f )

                dateExpVal = QgsExpression( self.attributesTableWidget.item(row, self.DATE_COLUMN).text() )
                dateExpVal.prepare( entityFields )
                date = dateExpVal.evaluate( f )

                interpExpVal = QgsExpression( self.attributesTableWidget.item(row, self.INTERP_COLUMN).text() )
                interpExpVal.prepare( entityFields )
                interp = interpExpVal.evaluate( f )

                prop = self.attributesTableWidget.item(row, self.PROPERTY_COLUMN).text()
                result = self.main.runQuery('queries/basic_create_or_get_property_type', {'property_name': prop})
                prop_type_id = result.fetchone()['id']

                sql = 'INSERT INTO vtm.properties(entity_id, property_type_id, value, date, interpolation) VALUES( %(ent_id)s, %(prop_type_id)s , %(val)s , %(date)s, %(interp)s ) RETURNING id;'
                cursor.execute(sql, {'ent_id': ent_id , 'prop_type_id': prop_type_id,'val': val,'date': date,'interp': interp })

                QgsMessageLog.logMessage( 'attribute create created : '+str(cursor.fetchone()), 'VTM Slider')

        connection.commit()
        cursor.close()






        