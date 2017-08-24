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
    DATE_START_IF_UNKNOWN_COLUMN = 4
    DATE_END_IF_UNKNOWN_COLUMN = 5

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

        self.sourceLineEdit.setText( self.layer.name() )

        for f in self.main.entitiesTypeLayer.getFeatures():
            self.entityTypeComboBox.addItem( f.attribute('name'), f.id() )

        for f in self.main.sourcesLayer.getFeatures():
            self.sourceComboBox.addItem( f.attribute('name'), f.id() )

        for f in self.main.propertiesTypeLayer.getFeatures():
	        self.addAttributeTypeComboBox.addItem( f.attribute('name'), f.id() )

        if self.layer.hasGeometryType():
            propItem = QTableWidgetItem('geom')
            dateItem = QTableWidgetItem( str(self.main.currentDate()) )
            interpItem = QTableWidgetItem( '\'default\'' )
            valItem = QTableWidgetItem('geomToWKT( transform($geometry,\'{0}\',\'EPSG:4326\') )'.format(crs))
            startDateItem = QTableWidgetItem( str(self.main.currentDate()-100) )
            endDateItem = QTableWidgetItem( str(self.main.currentDate()+100) )

            self.attributesTableWidget.insertRow(0)
            self.attributesTableWidget.setItem(0,self.PROPERTY_COLUMN,propItem)
            self.attributesTableWidget.setItem(0,self.DATE_COLUMN,dateItem)
            self.attributesTableWidget.setItem(0,self.INTERP_COLUMN,interpItem)
            self.attributesTableWidget.setItem(0,self.VALUE_COLUMN,valItem)
            self.attributesTableWidget.setItem(0,self.DATE_START_IF_UNKNOWN_COLUMN,startDateItem)
            self.attributesTableWidget.setItem(0,self.DATE_END_IF_UNKNOWN_COLUMN,endDateItem)


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
        dateItem = QTableWidgetItem( str(self.main.currentDate()) )
        interpItem = QTableWidgetItem( '\'default\'' )
        valItem = QTableWidgetItem( 'value' )
        startDateItem = QTableWidgetItem( str(self.main.currentDate()-100) )
        endDateItem = QTableWidgetItem( str(self.main.currentDate()+100) )

        self.attributesTableWidget.insertRow(self.attributesTableWidget.rowCount())

        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.PROPERTY_COLUMN,propItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.DATE_COLUMN,dateItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.INTERP_COLUMN,interpItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.VALUE_COLUMN,valItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.DATE_START_IF_UNKNOWN_COLUMN,startDateItem)
        self.attributesTableWidget.setItem(self.attributesTableWidget.rowCount()-1,self.DATE_END_IF_UNKNOWN_COLUMN,endDateItem)

    def removeProperty(self):
        self.attributesTableWidget.removeRow( self.addAttributeTypeComboBox.currentIndex() )

    def currentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentColumn in [self.DATE_COLUMN, self.INTERP_COLUMN, self.VALUE_COLUMN, self.DATE_START_IF_UNKNOWN_COLUMN, self.DATE_END_IF_UNKNOWN_COLUMN]:
            self.attributeExpressionButton.setEnabled(True)
        else:
            self.attributeExpressionButton.setEnabled(False)

    def getCount(self):
        if self.selectionOnlyCheckBox.isChecked():
            return self.layer.selectedFeatureCount()
        else:
            return self.layer.featureCount()

    def updateFeatureCountLabel(self):
        self.featureCountLabel.setText( 'You are going to load {0} features'.format( self.getCount() ) )


    def process(self):        
        # Here we do the actual loading

        progress = QProgressDialog("Importing features...", "Abort", 0, self.getCount(), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.raise_()

        featureIterator = None
        if self.selectionOnlyCheckBox.isChecked():
            featureIterator = self.layer.selectedFeaturesIterator()
        else:
            featureIterator = self.layer.getFeatures()

        connection = self.main.getConnection()
        cursor = connection.cursor()

        entityFields = self.main.entitiesLayer.pendingFields()

        i=0
        for f in featureIterator:
            i+=1
            progress.setValue(i)
            if progress.wasCanceled():
                break


            QgsMessageLog.logMessage( 'importing feature {0}'.format( f.id() ),'VTM Slider' )

            

            expName = QgsExpression( self.entityNameLineEdit.text() )
            expName.prepare( entityFields )
            ent_name = expName.evaluate( f )

            ent_type = self.entityTypeComboBox.itemText( self.entityTypeComboBox.currentIndex() ) if self.entityExistingRadioButton.isChecked() else self.entityTypeLineEdit.text()

            source_name = self.sourceComboBox.itemText( self.sourceComboBox.currentIndex() ) if self.sourceExistingRadioButton.isChecked() else self.sourceLineEdit.text()


            # 2. Creation of the properties

            for row in range(0, self.attributesTableWidget.rowCount()):

                valueExpVal = QgsExpression( self.attributesTableWidget.item(row, self.VALUE_COLUMN).text() )
                valueExpVal.prepare( entityFields )
                value = valueExpVal.evaluate( f )
                if isinstance(value,QPyNullVariant): value = None

                dateExpVal = QgsExpression( self.attributesTableWidget.item(row, self.DATE_COLUMN).text() )
                dateExpVal.prepare( entityFields )
                date = dateExpVal.evaluate( f )
                if isinstance(date,QPyNullVariant): date = None

                interpExpVal = QgsExpression( self.attributesTableWidget.item(row, self.INTERP_COLUMN).text() )
                interpExpVal.prepare( entityFields )
                interp = interpExpVal.evaluate( f )
                if isinstance(interp,QPyNullVariant): interp = None

                startExpVal = QgsExpression( self.attributesTableWidget.item(row, self.DATE_START_IF_UNKNOWN_COLUMN).text() )
                startExpVal.prepare( entityFields )
                start = startExpVal.evaluate( f )
                if isinstance(start,QPyNullVariant): start = None

                endExpVal = QgsExpression( self.attributesTableWidget.item(row, self.DATE_END_IF_UNKNOWN_COLUMN).text() )
                endExpVal.prepare( entityFields )
                end = endExpVal.evaluate( f )
                if isinstance(end,QPyNullVariant): end = None

                prop_name = self.attributesTableWidget.item(row, self.PROPERTY_COLUMN).text()

                sql = 'SELECT vtm.insert_properties_helper(%(ent_name)s, %(ent_type)s, %(source_name)s, %(prop_name)s, %(date)s, %(interp)s, %(value)s, %(start)s, %(end)s);'

                cursor.execute(sql, {'ent_name': ent_name, 'ent_type':ent_type, 'source_name':source_name, 'prop_name': prop_name,'value': value,'date': date,'interp': interp,'start': start,'end': end })

                QgsMessageLog.logMessage( 'attribute create created : '+str(cursor.fetchone()), 'VTM Slider')

        connection.commit()
        cursor.close()






        