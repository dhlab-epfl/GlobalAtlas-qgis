from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

myDialog = None

propertyField = None
valueField = None

def formOpen(dialog,layer,featureid):
	global myDialog
	global nameField
	global autoKeyValueMessage
	myDialog = dialog

	propertyField = dialog.findChild(QComboBox,"property_type_id")
	valueField = dialog.findChild(QLineEdit,"value")
	buttonBox = dialog.findChild(QDialogButtonBox,"buttonBox")

	
	if layer.hasGeometryType():
		propertyField.setEnabled(False)
		valueField.setEnabled(False)


	# Disconnect the signal that QGIS has wired up for the dialog to the button box.
	#buttonBox.accepted.disconnect(myDialog.accept)

	# Wire up our own signals.
	#buttonBox.accepted.connect(validate)
	#buttonBox.rejected.connect(myDialog.reject)

#def validate():
  # Make sure that the name field isn't empty.
	#if not nameField.text().length() > 0:
	#	msgBox = QMessageBox()
	#	msgBox.setText("Name field can not be null.")
	#	msgBox.exec_()
	#else:
		# Return the form as accpeted to QGIS.
		#myDialog.accept()