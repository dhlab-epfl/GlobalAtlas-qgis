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

import psycopg2
import psycopg2.extensions

from qgis.core import *
from qgis.gui import *

import os.path
import time


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

            if self.euratlasCitiesCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.verboseQuery('insertion of Euratlas cities for year {0}'.format(year), 'import/euratlas_cities', {'year':year})
                    self.main.commit()

            if self.euratlasDataCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.verboseQuery('insertion of Euratlas countries for year {0}'.format(year), 'import/euratlas', {'year':year})
                    self.main.commit()

            if self.euratlasEdgesGenCacheCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.verboseQuery('generation of Euratlas topological data for year {0} (this can take >2 min)'.format( psycopg2.extensions.AsIs(year) ), 'import/euratlas_edges_compute_cache', {'year':year})
                    self.main.commit()

            if self.euratlasEdgesLoadCacheCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.verboseQuery('insertion of Euratlas topological data for year {0}'.format( psycopg2.extensions.AsIs(year) ), 'import/euratlas_edges_load_from_cache', {'year':year})
                    self.main.commit()

            if self.idlDraftDataCheckBox.isChecked():
                self.verboseQuery('insertion of IdL draft data','import/idl_draft')
                self.main.commit()

            if self.processUpdateDatesCheckBox.isChecked():

                result = self.verboseQuery('Recomputing geometries by borders', 'queries/select_all_entities')
                for i,rec in enumerate(result):
                    if i%1000 == 0:
                        self.printOutput( 'doing {0}...'.format( i ) )
                    self.main.runQuery('queries/gbb_compute_geometries', {'entity_id': rec['id']})
                self.main.commit()


                result = self.verboseQuery('Recomputing dates', 'queries/select_all_properties_type_by_entity')
                for i,rec in enumerate(result):
                    if i%1000 == 0:
                        self.printOutput( 'doing {0}...'.format( i ) )
                    self.main.runQuery('queries/basic_compute_dates', {'entity_id': rec['entity_id'], 'property_type_id': rec['property_type_id']})
                self.main.commit()

            self.printOutput( '\nFinished' )
            self.main.commit()

        except psycopg2.ProgrammingError, e:
            self.setOutputError()
            self.printOutput( 'SQL error : {0}'.format(repr(e)) )

    def resetOutput(self):
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

    def setOutputError(self):
        self.outputTextEdit.setStyleSheet('color: red')

    def printOutput(self, text):
        self.outputTextEdit.appendPlainText( text )
        self.outputTextEdit.verticalScrollBar().setValue(self.outputTextEdit.verticalScrollBar().maximum())
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
        start_time = time.time()
        self.printOutput( '\n... starting '+text )
        result = self.main.runQuery(query, params)
        self.printOutput( 'Finished {0} (in {1} seconds)'.format(text, str(time.time()-start_time) ) )
        return result