import sys
import os
from PyQt4 import QtCore, QtGui
from DOE_message_form import Ui_MainWindow

# Constants
title = "DOE Runs"
PYTHONDIR="/cadshr/doe/version5/python";
icon = PYTHONDIR+"/DOE_message/images/Icon_Hankook.ico"
logo = PYTHONDIR+"/DOE_message/images/Logo_Hankook.png"

#####################################################################################################################################

class MainApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):

        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

#       Page Initialization
        self.setWindowTitle(title)
        self.lblTitle.setPixmap(QtGui.QPixmap(logo))
#        self.setWindowIcon(QtGui.QIcon(icon))

#       Message execution
        self.cmdOK.clicked.connect(self.ExitMessage)

    def ExitMessage(self):
        exit()


#####################################################################################################################################

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainApp()
#    window.move(window.width(),window.height())
    window.show()
    sys.exit(app.exec_())


