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

            self.main.runQuery('install/database_install_0_schema')
            self.printOutput( 'Schema installed' )

            self.main.runQuery('install/database_install_1_functions')
            self.printOutput( 'Functions installed' )

            self.main.runQuery('install/database_install_A_main')
            self.printOutput( 'Main structure installed' )

            self.main.runQuery('install/database_install_B_view-for-qgis')
            self.printOutput( 'QGIS view installed' )

            if self.dummyDataCheckBox.isChecked():
                self.main.runQuery('import/dummy_data')
                self.printOutput( 'Dummy data inserted' )

            if self.euratlasDataCheckBox.isChecked():
                self.main.runQuery('import/euratlas',{'from_date':self.euratlasFromDateSpinBox.value(), 'to_date':self.euratlasToDateSpinBox.value()})
                self.printOutput( 'Euratlas data inserted' )

            if self.euratlasEdgesDataCheckBox.isChecked():
                for year in range(self.euratlasFromDateSpinBox.value(),self.euratlasToDateSpinBox.value()+1,100):
                    self.printOutput( 'Start insertion of euratlas edges for year {0} (this can take >2 min)'.format(year) )
                    self.main.runQuery('import/euratlas_edges', {'year':year})
                    self.printOutput( 'Euratlas edges data inserted for year {0}'.format(year) )
                    self.main.commit()

            if self.idlDraftDataCheckBox.isChecked():
                self.main.runQuery('import/idl_draft')
                self.printOutput( 'IdL draft data inserted' )

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