import os
import sys
from xml.etree.ElementTree import TreeBuilder

# from hid import HIDException
import utils

from PyQt6.QtCore import (Qt, pyqtSlot, QTimer, QThreadPool)
from PyQt6.QtWidgets import (QMainWindow, QPushButton,
        QHBoxLayout, QVBoxLayout, QApplication, QToolTip, QMessageBox,
        QLabel, QCheckBox, QSystemTrayIcon, QStyle, QMenu)
from PyQt6.QtGui import (QFont, QAction, QIcon, QKeyEvent)


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initVars()

        self.initWorkers()
        
        self.initUI()


        # here we initialize the hid class
        abspath = os.path.abspath(__file__)
        dirname = os.path.dirname(abspath)
        os.chdir(dirname)
        config = os.path.join(dirname, 'config.ini')
        # this actually connects us to the device
        # but there's no way for the device to know that
        # without sending something to it.
        self.device = utils.QMKDevice(config)
        self.clear_screen()
        
    def initVars(self):
        self.military_time = False

        self.stateAutoSwitch = True
        self.stateHIDConnect = False
        self.hasStateChanged = False
        self.previousActiveState = None

        self.previousTime = None
        self.timeChange = False
        self.previousWeatherData = ''

    def initUI(self):
        self.toolTips()
        # self.quitButton()
        self.initLabels()
        self.initCheckbox()
        self.initToggleButton()
        self.initSysTray()

        self.setStatusBar()
        
        self.statusBar().showMessage("ready")

        self.resize(350, 250)
        self.center()
        self.setWindowTitle('doves')
        self.show()

    def initSysTray(self):
        self.tray_icon = QSystemTrayIcon(self)

        menu = QMenu("doves")
        openAction = QAction("open", self)
        openAction.triggered.connect(self._sysTrayOpen)
        menu.addAction(openAction)

        self.tray_icon.setContextMenu(menu)

        icon = QIcon("icons/dove.png")
        self.tray_icon.setIcon(icon)
        self.setVisible(True)

        self.tray_icon.activated.connect(self._trayIconClicked)

    def _sysTrayOpen(self):
        self.show()
        self.tray_icon.hide()

    def _trayIconClicked(self, reason):
        if reason == self.tray_icon.ActivationReason.DoubleClick:
            self.show()
            self.tray_icon.hide()
        elif reason == self.tray_icon.ActivationReason.Context:
            pass


    def initWorkers(self):
        self.threadpool = QThreadPool()

        self.start_workers()

    def start_workers(self):
        self._startActiveWorker()
        self._startTimeWorker()
        self._startWeatherWorker()

    def _startActiveWorker(self):
        '''
        this returns the active window every second

        connects to slot _processActiveSignal
        '''
        self.activeSignal = utils.QMKActiveSignal()
        self.activeSignal.result.connect(self._processActiveSignal)
        self._loopActiveWorker()

    def _loopActiveWorker(self):
        active = utils.QMKActiveWorker(signals=self.activeSignal)

        self.threadpool.start(active)
        QTimer.singleShot(1000, self._loopActiveWorker)

    @pyqtSlot(str)
    def _processActiveSignal(self, data):
        '''
        decides what to do with the current active window
        '''

        # this is so if you manually change your layer, it doesn't automatically switch it back right away
        self.hasStateChanged = data != self.previousActiveState
        self.previousActiveState = data if data != self.previousActiveState else self.previousActiveState
        
        self.activeLabel.setText(f"Active: {data}")
        if self.stateHIDConnect and self.stateAutoSwitch and self.hasStateChanged:
            if data in ["Risk of Rain 2.exe", "r5apex.exe"]:
                self.device.set_layer(layer=2)
            elif data in ["VALORANT-Win64-Shipping.exe"]:
                self.device.set_layer(layer=1)
            else:
                self.device.set_layer(layer=0)

    def _startTimeWorker(self):
        self.timeSignal = utils.TimeSignal()
        self.timeSignal.result.connect(self._processTimeSignal)
        self._loopTimeSignal()

    def _loopTimeSignal(self):
        current_time = utils.TimeWorker(signals=self.timeSignal)

        self.threadpool.start(current_time)
        QTimer.singleShot(1000, self._loopTimeSignal)

    def _startWeatherWorker(self):
        self.weatherSignal = utils.Weather()
        self.weatherSignal.result.connect(self._processWeatherSignal)
        self._loopWeatherSignal()

    def clear_screen(self):
        for index in range(0, 16):
            self.device.send_line(line=index, data='')

    @pyqtSlot(str)
    def _processWeatherSignal(self, data):
        weather_data_diff = self.previousWeatherData != data
        if weather_data_diff and self.stateHIDConnect and self.device:
            self.device.send_line(line=8, data=data)
            self.previousWeatherData = data


    def _loopWeatherSignal(self):
        weather = utils.WeatherWorker(signals=self.weatherSignal)

        self.threadpool.start(weather)
        QTimer.singleShot(1000, self._loopWeatherSignal)

    @pyqtSlot(str)
    def _processTimeSignal(self, data):
        self.timeChange = data != self.previousTime
        self.previousTime = data if data != self.previousTime else self.previousTime
        
        if self.cbTime.isChecked() and self.stateHIDConnect and self.timeChange:
            # write time to device
            if not self.military_time:
                split_data = data.split(':')
                hours = int(split_data[0])
                if (hours > 12):
                    hours = hours - 12
                    if hours < 10:
                        hours = '0' + str(hours)
                    else:
                        hours = str(hours)
                    data = hours + ':' + split_data[-1]
                    
                new_lines = self.active_lines
                new_lines.append(2)
                self.active_lines = new_lines

            self.device.send_line(line=1, data=data)
        else:
            pass
            # try:
            #     self.device.clear_line(line=8)
            # except HIDException:
            #     pass
        return
        

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
        if self.cbSysTray.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.show()
        else:
            self.device.close()
        return
        reply = QMessageBox.question(self, "Message", 
                    "Are you sure to quit?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.device.close()
        else:
            event.ignore()
    
    def center(self):
        """
        useful for center the window. helpful. and will be used
        """
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


        self.activeLabel = QLabel(f"Active: unknown", self)
        self.activeLabel.move(10, 100) 

    def keyPressEvent(self, a0) -> None:
        '''
        handle key event example
        '''
        if a0.key() == Qt.Key.Key_Escape.value:
            self.close()

    def initCheckbox(self):
        cb = QCheckBox("Auto Switch", self)
        cb.move(10, 35)
        cb.setChecked(self.stateAutoSwitch)
        cb.stateChanged.connect(self.autoSwitchChange)

        self._initSysTrayCheckbox()
        self._initTimeWorkerCheckbox()

    def _initSysTrayCheckbox(self):
        '''
        cbSysTray = checkbox system tray
        '''
        self.cbSysTray = QCheckBox("Minimize to Tray", self)
        self.cbSysTray.move(150, 35)

    
    def autoSwitchChange(self, state):
        '''
        eventually use to toggle features on host app
        '''
        if state == Qt.CheckState.Checked.value:
            self.stateAutoSwitch = True
        else:
            self.stateAutoSwitch = False

    def initToggleButton(self):
        hidToggle = QPushButton("hid", self)
        hidToggle.setCheckable(True)
        hidToggle.move(10, 55)
        hidToggle.clicked[bool].connect(self.toggleHIDconnect)

    def toggleHIDconnect(self, pressed):
        if pressed:
            self.device.write("ping") # this can be anything
            self.stateHIDConnect = True
        else:
            self.device.disconnect()
            self.stateHIDConnect = False

    def _initTimeWorkerCheckbox(self):
        self.cbTime = QCheckBox("HID time", self)
        self.cbTime.move(150, 50)
    

def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
