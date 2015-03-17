# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# Basic dependencies
import os.path

class VTMHelp(QDialog):

    def __init__(self):
        QDialog.__init__(self)

        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self.helpFile = os.path.join(os.path.dirname(__file__),'README.html')
        
        self.setWindowTitle('VeniceTimeMachine')

        txt = QTextBrowser()
        txt.setReadOnly(True)
        txt.setSearchPaths([os.path.dirname(__file__)])
        txt.setOpenExternalLinks(True)
        txt.setText( open(self.helpFile, 'r').read() )

        cls = QPushButton('Close')

        cls.pressed.connect(self.accept)

        lay = QVBoxLayout()
        lay.addWidget(txt)
        lay.addWidget(cls)

        self.setLayout(lay)
