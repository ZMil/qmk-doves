import os
import sys
import utils

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QMainWindow, QPushButton,
        QHBoxLayout, QVBoxLayout, QApplication, QToolTip, QMessageBox,
        QLabel, QCheckBox)
from PyQt6.QtGui import (QFont, QAction, QIcon, QKeyEvent)
from configparser import ConfigParser

class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

        # here we initialize the hid class
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        os.chdir(dirname)
        config = os.path.join(dirname, 'config.ini')

        self.device = utils.QMKDevice(config)
        
        
    def initUI(self):
        self.toolTips()
        self.quitButton()
        self.initLabels()
        self.initCheckbox()
        self.initToggleButton()

        self.setStatusBar()
        
        self.statusBar().showMessage("ready")

        self.resize(350, 250)
        self.center()
        self.setWindowTitle('doves')
        self.show()

    def toolTips(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip("QMK toolkit")

    def quitButton(self):
        """
        demo quit button, won't live here forever
        """
        btn = QPushButton("quit", self)
        btn.clicked.connect(QApplication.instance().quit)
        btn.resize(btn.sizeHint())
        btn.move(10, 75)

    def closeEvent(self, event):
        """
        eventually should become quit or minimize to taskbar
        """
        reply = QMessageBox.question(self, "Message", 
                    "Are you sure to quit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.device.close()
        else:
            event.ignore()
    
    def center(self):
        """
        useful for center the window. helpful. and will be used"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setStatusBar(self):
        menubar = self.menuBar()
        exitAct = self.statusBarExit()

        fileMenu = menubar.addMenu('&file')
        fileMenu.addAction(exitAct)

    def statusBarExit(self):
        exitAct = QAction(QIcon("icons/close.png"), "&exit", self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('exit application')
        exitAct.triggered.connect(QApplication.instance().quit)
        return(exitAct)

    def initLabels(self):
        lbl = QLabel("QMK toolkit", self)
        lbl.move(10, 20)

    def keyPressEvent(self, a0) -> None:
        '''
        handle key event example
        '''
        if a0.key() == Qt.Key.Key_Escape.value:
            self.close()

    def initCheckbox(self):
        cb = QCheckBox("Auto Switch", self)
        cb.move(10, 35)
        cb.toggle()
        cb.stateChanged.connect(self.autoSwitchChange)
    
    def autoSwitchChange(self, state):
        '''
        eventually use to toggle features on host app
        '''
        if state == Qt.CheckState.Checked.value:
            print("value checked")
            pass
        else:
            pass

    def initToggleButton(self):
        hidToggle = QPushButton("hid", self)
        hidToggle.setCheckable(True)
        hidToggle.move(10, 55)
        hidToggle.clicked[bool].connect(self.toggleHIDconnect)

    def toggleHIDconnect(self, pressed):
        if pressed:
            self.device.write("hi") # this can be anything
        else:
            self.device.disconnect()

def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
