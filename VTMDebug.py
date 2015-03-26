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
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

        for layer in self.iface.legendInterface().layers():
            self.outputTextEdit.appendPlainText( '{0}:\t\t{1}'.format(layer.name(),layer.id()) )


    def doReset(self):
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

        try:

            self.main.runQuery('install/database_install_0_schema')
            self.main.commit()
            self.outputTextEdit.appendPlainText( 'Schema installed' )

            self.main.runQuery('install/database_install_1_functions')
            self.main.commit()
            self.outputTextEdit.appendPlainText( 'Functions installed' )

            self.main.runQuery('install/database_install_A_main')
            self.main.commit()
            self.outputTextEdit.appendPlainText( 'Main structure installed' )

            self.main.runQuery('install/database_install_B_view-for-qgis')
            self.main.commit()
            self.outputTextEdit.appendPlainText( 'QGIS view installed' )

            if self.dummyDataCheckBox.isChecked():
                self.main.runQuery('import/dummy_data')
                self.main.commit()
                self.outputTextEdit.appendPlainText( 'Dummy data inserted' )

            if self.euratlasDataCheckBox.isChecked():
                self.main.runQuery('import/euratlas')
                self.main.commit()
                self.outputTextEdit.appendPlainText( 'Euratlas data inserted' )

            if self.euratlasEdgesDataCheckBox.isChecked():
                self.main.runQuery('import/euratlas_edges')
                self.main.commit()
                self.outputTextEdit.appendPlainText( 'Euratlas edges data inserted' )

            if self.idlDraftDataCheckBox.isChecked():
                self.main.runQuery('import/idl_draft')
                self.main.commit()
                self.outputTextEdit.appendPlainText( 'IdL draft data inserted' )


        except Exception, e:
            self.outputTextEdit.setStyleSheet('color: red')
            self.outputTextEdit.appendPlainText( '{0}'.format(str(e)) )



    def doViewSettings(self):
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

        for s in ['VTM Slider/username','VTM Slider/password']:
            self.outputTextEdit.appendPlainText( '{0}:\t{1}'.format(s,str(QSettings().value(s))) ) 

    def doDeleteSettings(self):
        self.outputTextEdit.clear()
        self.outputTextEdit.setStyleSheet('')

        QSettings().remove("VTM Slider")

        self.outputTextEdit.appendPlainText( 'Settings removed' )