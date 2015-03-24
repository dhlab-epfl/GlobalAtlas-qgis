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

            with self.main.connection.cursor() as cursor:

                sql = open( os.path.join(self.main.plugin_dir,'sql','database_install_0_schema.sql') ).read()
                cursor.execute( sql )
                self.main.connection.commit()

                self.outputTextEdit.appendPlainText( 'Schema installed' )


                sql = open( os.path.join(self.main.plugin_dir,'sql','database_install_1_functions.sql') ).read()
                cursor.execute( sql )
                self.main.connection.commit()

                self.outputTextEdit.appendPlainText( 'Functions installed' )


                sql = open( os.path.join(self.main.plugin_dir,'sql','database_install_A_main.sql') ).read()
                cursor.execute( sql )
                self.main.connection.commit()

                self.outputTextEdit.appendPlainText( 'Main structure installed' )


                sql = open( os.path.join(self.main.plugin_dir,'sql','database_install_B_view-for-qgis.sql') ).read()
                cursor.execute( sql )
                self.main.connection.commit()

                self.outputTextEdit.appendPlainText( 'QGIS view installed' )

                if self.dummyDataCheckBox.isChecked():

                    sql = open( os.path.join(self.main.plugin_dir,'sql','database_install_C_dummy_data.sql') ).read()
                    cursor.execute( sql )
                    self.main.connection.commit()

                    self.outputTextEdit.appendPlainText( 'Dummy data inserted' )

                if self.euratlasDataCheckBox.isChecked():

                    sql = open( os.path.join(self.main.plugin_dir,'sql','import','euratlas.sql') ).read()
                    cursor.execute( sql )
                    self.main.connection.commit()

                    self.outputTextEdit.appendPlainText( 'Euratlas data inserted' )

                if self.idlDraftDataCheckBox.isChecked():

                    sql = open( os.path.join(self.main.plugin_dir,'sql','import','idl_draft.sql') ).read()
                    cursor.execute( sql )
                    self.main.connection.commit()

                    self.outputTextEdit.appendPlainText( 'IdL draft data inserted' )

                else:
                    pass


                self.main.connection.commit()


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