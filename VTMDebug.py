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


class VTMDebug(QDialog):

    def __init__(self, iface, main):

        self.iface = iface
        self.main = main

        QDialog.__init__(self)
        uic.loadUi(os.path.dirname(__file__)+'/ui/debug.ui', self)

        self.showIdButton.pressed.connect(self.doShowIds)
        self.resetButton.pressed.connect(self.doReset)
        self.viewSettingsButton.pressed.connect(self.doViewSettings)
        self.deleteSettingsButton.pressed.connect(self.doDeleteSettings)

    def doShowIds(self):
        self.resetOutput()

        for layer in self.iface.legendInterface().layers():
            self.printOutput( '{0}:\t\t{1}'.format(layer.name(),layer.id()) )


    def doReset(self):
        self.resetOutput()

        try:

            if self.reinstallCheckBox.isChecked():

                self.verboseQuery('installation of schema','install/01_schema')

                self.verboseQuery('installation of functions','install/02_functions')

                self.verboseQuery('installation of the main structure','install/03_main')

                self.verboseQuery('installation of the geometry extension', 'install/03b_geom_extension')

                self.verboseQuery('installation of the view for QGIS','install/04_view_for_qgis')

                self.verboseQuery('insertion of the basic types','install/05_types')

                self.main.commit()

            if self.dummyDataCheckBox.isChecked():
                self.verboseQuery('insertion of dummy data','import/dummy_data')               
                self.main.commit()

            if self.dummyBordersDataCheckBox.isChecked():
                self.verboseQuery('insertion of dummy data (borders)','import/dummy_data_borders')               
                self.main.commit()



            if self.euratlasDataCheckBox.isChecked():
                self.verboseQuery('insertion of Euratlas data','import/euratlas',{'from_date':self.euratlasFromDateSpinBox.value(), 'to_date':self.euratlasToDateSpinBox.value()})            
                self.main.commit()

            if self.euratlasEdgesDataCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.verboseQuery('insertion of Euratlas topological data for year {0} (this can take >2 min)'.format(year), 'import/euratlas_edges', {'year':year})
                    self.main.commit()

            if self.idlDraftDataCheckBox.isChecked():
                self.verboseQuery('insertion of IdL draft data','import/idl_draft')
                self.main.commit()

            if self.processUpdateDatesCheckBox.isChecked():
                self.printOutput( 'Recomputing dates' )
                result = self.main.runQuery('queries/select_all_properties_type_by_entity')
                for rec in result:
                    self.main.runQuery('queries/compute_dates', {'entity_id': rec['entity_id'], 'property_type_id': rec['property_type_id']})
                self.main.commit()

            self.printOutput( 'Finished' )
            self.main.commit()


        except Exception, e:
            self.setOutputError()
            self.printOutput( '{0}'.format(str(e)) )

    def resetOutput(self):
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

    def setOutputError(self):
        self.outputTextEdit.setStyleSheet('color: red')

    def printOutput(self, text):
        self.outputTextEdit.appendPlainText( text )
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def doViewSettings(self):
        self.resetOutput()

        for s in ['VTM Slider/username','VTM Slider/password']:
            self.printOutput( '{0}:\t{1}'.format(s,str(QSettings().value(s))) ) 

    def doDeleteSettings(self):
        self.resetOutput()

        QSettings().remove("VTM Slider")

        self.printOutput( 'Settings removed' )

    def verboseQuery(self,text,query,params={}):
        self.printOutput( '\n... starting '+text )
        self.main.runQuery(query, params)
        self.printOutput( 'Finished '+text )
                