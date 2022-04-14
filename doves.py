

import sys

from PyQt6.QtWidgets import (QMainWindow, QPushButton,
        QHBoxLayout, QVBoxLayout, QApplication, QToolTip, QMessageBox)
from PyQt6.QtGui import (QFont)


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

        
    def initUI(self):
        self.toolTips()
        self.quitButton()
        
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
        btn.move(50,50)

    def closeEvent(self, event):
        """
        eventually should become quit or minimize to taskbar
        """
        reply = QMessageBox.question(self, "Message", 
                    "Are you sure to quit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
    
    def center(self):
        """
        useful for center the window. helpful. and will be used"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
