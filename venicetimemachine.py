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

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import * 
from PyQt4.QtWebKit import *
from qgis.core import *
from VTMToolBar import VTMToolBar

import os.path


class VeniceTimeMachine:

    instance = None

    def __init__(self, iface):

        self.plugin_dir = os.path.dirname(__file__)
        
        # Save reference to the QGIS interface
        self.iface = iface
        #self.sqlManager = VTMSqlManager(self.iface)
        VeniceTimeMachine.instance = self

    def initGui(self):
        """ Put your code here and remove the pass statement"""

        self.dockwidget = VTMToolBar(self.iface)
        self.iface.mainWindow().addDockWidget(Qt.TopDockWidgetArea,self.dockwidget)
        self.dockwidget.show()

    def unload(self):
        self.iface.mainWindow().removeDockWidget(self.dockwidget)



