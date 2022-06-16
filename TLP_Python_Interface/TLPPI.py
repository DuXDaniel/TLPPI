import numpy as np
import math as math
import matplotlib
import matplotlib.pyplot as plt
import time
import tqdm
import sys
import json
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, QThread, pyqtSignal, QRunnable
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDial, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar,
                             QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QHeaderView, QSpacerItem, QTableWidgetItem,
                             QTableWidgetSelectionRange, QAbstractItemView, QFileDialog, QPlainTextEdit)
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

try:
    from MDT_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)

def main(argv):

    #appctxt = ApplicationContext()
    app = QApplication([])
    gallery = WidgetGallery()
    gallery.show()
    app.exec()
    #sys.exit(appctxt.app.exec())

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        self.serialNumber = 0
        self.limitVoltage = 0
        self.isMoving = 0
        self.xVoltage = 0
        self.yVoltage = 0
        self.zVoltage = 0
        self.xValue = 0
        self.yValue = 0
        self.zValue = 0
        self.padStep = 0
        self.pzhdl = {}
        self.padControlToggle = 0

        super(WidgetGallery, self).__init__(parent)

        self.setMinimumSize(500, 500)
        self.setWindowTitle("ThorLabs Piezocontroller Python Interface")

        self.overallWidget()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.fullWidget, 1, 0, 1, 1)

        self.setLayout(mainLayout)

        self.changeStyle('windowsvista')

        self.padThread = QThread()
        self.padTracker = padWorker(self.serialNumber, self.pzhdl, self.freeControlButton, self.xVoltage, self.yVoltage, self.zVoltage, self.padStep, self.limitVoltage)
        self.padTracker.comms.connect(self.updateStatus.appendPlainText)
        self.padTracker.moveToThread(self.padThread)
        self.padThread.started.connect(self.padTracker.run)
        self.padTracker.disconnect.connect(self.padThread.quit)
        self.padTracker.disconnect.connect(self.padTracker.deleteLater)
        self.padThread.finished.connect(self.padThread.deleteLater)

    def closeEvent(self, event):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            mdtClose(self.pzhdl)

        # check gamepad reading
        if (True):
            return

    def overallWidget(self):

        self.fullWidget = QWidget()
        self.fullWidgetLayout = QGridLayout()

        self.connectGroupBox = QGroupBox("Connect/Disconnect")
        self.statusGroupBox = QGroupBox("Device Status")
        self.controlGroupBox = QGroupBox("Device Control")

        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.connectPZCTRL)

        self.connectSpacer = QSpacerItem(0,0,QSizePolicy.Expanding)

        self.disconnectButton = QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(self.disconnectPZCTRL)

        self.connectLayout = QGridLayout()
        self.connectLayout.addWidget(self.connectButton, 0, 0, 1, 1)
        self.connectLayout.addItem(self.connectSpacer, 0, 0, 1, 5)
        self.connectLayout.addWidget(self.disconnectButton, 0, 6, 1, 1)
        self.connectLayout.setVerticalSpacing(0)
        self.connectGroupBox.setLayout(self.connectLayout)

        self.serialText = QLabel("Serial No.: ")
        self.serialStatus = QLabel("")
        self.connectText = QLabel("Connection: ")
        self.connectStatus = QLabel("Off")
        self.vlimText = QLabel("Voltage Limit (V): ")
        self.vlimStatus = QLabel("0")
        self.movingText = QLabel("Moving: ")
        self.movingStatus = QLabel("No")
        self.updateText = QLabel("Status Updates:")
        self.updateStatus = QPlainTextEdit("")

        self.statusLayout = QGridLayout()
        self.statusLayout.addWidget(self.serialText, 0, 0, 1, 1)
        self.statusLayout.addWidget(self.serialStatus, 0, 1, 1, 1, alignment=Qt.AlignRight)
        self.statusLayout.addWidget(self.connectText, 1, 0, 1, 1)
        self.statusLayout.addWidget(self.connectStatus, 1, 1, 1, 1, alignment=Qt.AlignRight)
        self.statusLayout.addWidget(self.vlimText, 2, 0, 1, 1)
        self.statusLayout.addWidget(self.vlimStatus, 2, 1, 1, 1, alignment=Qt.AlignRight)
        self.statusLayout.addWidget(self.movingText, 3, 0, 1, 1)
        self.statusLayout.addWidget(self.movingStatus, 3, 1, 1, 1, alignment=Qt.AlignRight)
        self.statusLayout.addWidget(self.updateText, 0, 2, 1, 1)
        self.statusLayout.addWidget(self.updateStatus, 1, 2, 3, 1)
        self.statusLayout.setRowStretch(4,1)
        self.statusLayout.setVerticalSpacing(0)
        self.statusGroupBox.setLayout(self.statusLayout)

        self.xVSliderText = QLabel("X-Axis Voltage: ")
        self.xVSliderValueText = QLabel("")
        self.xVSlider = QSlider(Qt.Horizontal)
        self.xVSlider.setFocusPolicy(Qt.StrongFocus)
        self.xVSlider.setTickPosition(QSlider.TicksBothSides)
        self.xVSlider.setTickInterval(10000)
        self.xVSlider.setSingleStep(1)
        self.xVSlider.setMinimum(0)
        self.xVSlider.setMaximum(65536)
        self.xVSlider.sliderReleased.connect(self.moveXVSlider)

        self.yVSliderText = QLabel("X-Axis Voltage: ")
        self.yVSliderValueText = QLabel("")
        self.yVSlider = QSlider(Qt.Horizontal)
        self.yVSlider.setFocusPolicy(Qt.StrongFocus)
        self.yVSlider.setTickPosition(QSlider.TicksBothSides)
        self.yVSlider.setTickInterval(10000)
        self.yVSlider.setSingleStep(1)
        self.yVSlider.setMinimum(0)
        self.yVSlider.setMaximum(65536)
        self.yVSlider.sliderReleased.connect(self.moveYVSlider)

        self.zVSliderText = QLabel("X-Axis Voltage: ")
        self.zVSliderValueText = QLabel("")
        self.zVSlider = QSlider(Qt.Horizontal)
        self.zVSlider.setFocusPolicy(Qt.StrongFocus)
        self.zVSlider.setTickPosition(QSlider.TicksBothSides)
        self.zVSlider.setTickInterval(10000)
        self.zVSlider.setSingleStep(1)
        self.zVSlider.setMinimum(0)
        self.zVSlider.setMaximum(65536)
        self.zVSlider.sliderReleased.connect(self.moveZVSlider)

        self.freeControlButton = QPushButton("Pad Control")
        self.freeControlButton.setStyleSheet("background-color : lightgrey")
        self.freeControlButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.freeControlButton.setCheckable(True)
        self.freeControlButton.clicked.connect(self.togglePadControl)
        self.voltageStepText = QLabel("Voltage Step: ")
        self.voltageStepValueText = QLabel("")

        self.controlLayout = QGridLayout()
        self.controlLayout.addWidget(self.xVSliderText, 0, 0, 1, 1)
        self.controlLayout.addWidget(self.xVSliderValueText, 0, 1, 1, 1)
        self.controlLayout.addWidget(self.xVSlider, 1, 0, 1, 2)
        self.controlLayout.addWidget(self.yVSliderText, 2, 0, 1, 1)
        self.controlLayout.addWidget(self.yVSliderValueText, 2, 1, 1, 1)
        self.controlLayout.addWidget(self.yVSlider, 3, 0, 1, 2)
        self.controlLayout.addWidget(self.zVSliderText, 4, 0, 1, 1)
        self.controlLayout.addWidget(self.zVSliderValueText, 4, 1, 1, 1)
        self.controlLayout.addWidget(self.zVSlider, 5, 0, 1, 2)
        self.controlLayout.addWidget(self.freeControlButton, 0, 2, 4, 2)
        self.controlLayout.addWidget(self.voltageStepText, 5, 2, 1, 1)
        self.controlLayout.addWidget(self.voltageStepValueText, 5, 3, 1, 1)
        self.controlLayout.setVerticalSpacing(0)
        self.controlGroupBox.setLayout(self.controlLayout)

        self.fullWidgetLayout.addWidget(self.connectGroupBox, 0, 0, 1, 1)
        self.fullWidgetLayout.addWidget(self.statusGroupBox, 1, 0, 1, 1)
        self.fullWidgetLayout.addWidget(self.controlGroupBox, 2, 0, 1, 1)
        self.fullWidgetLayout.setRowStretch(3,1)
        self.fullWidget.setLayout(self.fullWidgetLayout)
        
    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def convertVoltageToVal(curVoltage):
        return (65536 * (curVoltage/self.limitVoltage))
    
    def convertValToVoltage(curVal):
        return ((curVal/65536) * self.limitVoltage)

    def connectPZCTRL(self):
        try:
            devs = mdtListDevices()
            if(len(devs)<=0):
                self.updateStatus.appendPlainText("No controllers found.")
                self.updateStatus.ensureCursorVisible()
                return -1

            for mdt in devs:
                self.serialNumber = mdt[0]
                if (mdtIsOpen(self.serialNumber) == 1):
                    self.updateStatus.appendPlainText("Connection to " + str(self.serialNumber) + " already established")
                    self.updateStatus.ensureCursorVisible()
                    return -1
                else:
                    self.pzhdl = mdtOpen(self.serialNumber,115200,3)
                    if(self.pzhdl < 0):
                        self.updateStatus.appendPlainText("Connection attempt to " + str(self.serialNumber) + " failed")
                        self.updateStatus.ensureCursorVisible()
                        mdtClose(self.pzhdl)
                        return -1
                    else:
                        self.updateStatus.appendPlainText("Connection attempt to " + str(self.serialNumber) + " success")
                        self.updateStatus.ensureCursorVisible()

                    result = mdtGetLimtVoltage(self.pzhdl, self.limitVoltage)
                    if(result<0):
                        self.updateStatus.appendPlainText("Voltage limit retreival of " + str(self.serialNumber) + " failed")
                        self.updateStatus.ensureCursorVisible()
                        mdtClose(self.pzhdl)
                        return -1
                    else:
                        self.updateStatus.appendPlainText("Voltage limit retreival of " + str(self.serialNumber) + " success")
                        self.updateStatus.ensureCursorVisible()
                    return self.pzhdl # returns first controller found
        except:
            return -1
        
        self.serialStatus.setText(self.serialNumber)
        self.connectStatus.setText("On")
        self.vlimStatus.setText(self.limitVoltage)

        mdtGetXAxisVoltage(self.pzhdl, self.xVoltage)
        mdtGetYAxisVoltage(self.pzhdl, self.yVoltage)
        mdtGetZAxisVoltage(self.pzhdl, self.zVoltage)

        self.xVSliderValueText.setText(self.xVoltage)
        self.xValue = convertVoltageToVal(self.xVoltage)
        self.yVSliderValueText.setText(self.yVoltage)
        self.yValue = convertVoltageToVal(self.yVoltage)
        self.zVSliderValueText.setText(self.zVoltage)
        self.zValue = convertVoltageToVal(self.zVoltage)

        self.xVSlider.setValue(self.xValue)
        self.yVSlider.setValue(self.yValue)
        self.zVSlider.setValue(self.zValue)

        mdtGetVoltageAdjustmentResolution(self.pzhdl,self.padStep)
        self.voltageStepValueText.setText(self.padStep)

        self.voltageTracker()
    
    def disconnectPZCTRL(self):
        if ((self.serialNumber != 0) and (mdtIsOpen(self.serialNumber) == 1)):
            try:
                mdtClose(self.pzhdl)
                self.updateStatus.appendPlainText("Closure of " + str(self.serialNumber) + " success")
                self.updateStatus.ensureCursorVisible()
            except:
                self.updateStatus.appendPlainText("Closure of " + str(self.serialNumber) + " failed")
                self.updateStatus.ensureCursorVisible()
                return -1
        else:
            self.updateStatus.appendPlainText("No controller is connected.")
            self.updateStatus.ensureCursorVisible()
            return -1

        self.connectStatus.setText("Off")

    def voltageTracker(self):
        self.trackerThread = QThread()
        self.voltTracker = voltageWorker(self.serialNumber, self.pzhdl)
        self.voltTracker.xVSVT.connect(self.xVSliderValueText.setText)
        self.voltTracker.yVSVT.connect(self.xVSliderValueText.setText)
        self.voltTracker.zVSVT.connect(self.xVSliderValueText.setText)
        self.voltTracker.moveToThread(self.trackerThread)
        self.trackerThread.started.connect(self.voltTracker.run)
        self.voltTracker.disconnect.connect(self.trackerThread.quit)
        self.voltTracker.disconnect.connect(self.voltTracker.deleteLater)
        self.trackerThread.finished.connect(self.trackerThread.deleteLater)
        self.trackerThread.start()
    
    def moveXVSlider(self):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.updateStatus.appendPlainText("Moving piezostage...")
            self.updateStatus.ensureCursorVisible()
            self.xVoltage = self.convertValToVoltage(self.xVSlider.value)
            mdtSetXAxisVoltage(self.xVoltage)
            mdtGetXAxisVoltage(self.pzhdl, self.xVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def moveYVSlider(self):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.updateStatus.appendPlainText("Moving piezostage...")
            self.updateStatus.ensureCursorVisible()
            self.yVoltage = self.convertValToVoltage(self.yVSlider.value)
            mdtSetYAxisVoltage(self.yVoltage)
            mdtGetYAxisVoltage(self.pzhdl, self.yVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def moveZVSlider(self):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.updateStatus.appendPlainText("Moving piezostage...")
            self.updateStatus.ensureCursorVisible()
            self.zVoltage = self.convertValToVoltage(self.zVSlider.value)
            mdtSetZAxisVoltage(self.zVoltage)
            mdtGetZAxisVoltage(self.pzhdl, self.zVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def togglePadControl(self):
        if (self.freeControlButton.isChecked() and self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.freeControlButton.setStyleSheet("background-color : lightblue")
            self.padControlToggle = 1

            self.padThread.start()
        else:
            self.freeControlButton.setStyleSheet("background-color : lightgrey")
            self.padControlToggle = 0
        
        return -1

class padWorker(QThread):
    comms = pyqtSignal(str)
    disconnect = pyqtSignal()
    stepx = 0
    stepy = 0
    stepz = 0

    def __init__(self, serialNumber, pzhdl, toggleButton, xVoltage, yVoltage, zVoltage, padStep, limitVoltage):
        super().__init__()
        self.toggleButton = toggleButton
        self.serialNumber = serialNumber
        self.pzhdl = pzhdl
        self.xVoltage = xVoltage
        self.yVoltage = yVoltage
        self.zVoltage = zVoltage
        self.padStep = padStep
        self.limitVoltage = limitVoltage

    # establish connection to gamepad
    
    def run(self):
        while (self.toggleButton.isChecked()):
            
            # get active pad events
            
            # figure out how to increment voltage step with DPad
            # establish incDir
            # set steps to 1, -1, or 0

            if (stepx != 0):
                candidateVoltage = xVoltage + stepx*self.padStep
                if (candidateVoltage > self.limitVoltage):
                    mdtSetXAxisVoltage(self.pzhdl,self.limitVoltage)
                elif (candidateVoltage < 0):
                    mdtSetXAxisVoltage(self.pzhdl,0)
                else:
                    mdtSetXAxisVoltage(self.pzhdl,candidateVoltage)
            
            if (stepy != 0):
                candidateVoltage = yVoltage + stepy*self.padStep
                if (candidateVoltage > self.limitVoltage):
                    mdtSetYAxisVoltage(self.pzhdl,self.limitVoltage)
                elif (candidateVoltage < 0):
                    mdtSetYAxisVoltage(self.pzhdl,0)
                else:
                    mdtSetYAxisVoltage(self.pzhdl,candidateVoltage)

            if (stepz != 0):
                candidateVoltage = zVoltage + stepz*self.padStep
                if (candidateVoltage > self.limitVoltage):
                    mdtSetZAxisVoltage(self.pzhdl,self.limitVoltage)
                elif (candidateVoltage < 0):
                    mdtSetZAxisVoltage(self.pzhdl,0)
                else:
                    mdtSetZAxisVoltage(self.pzhdl,candidateVoltage)

            time.sleep(0.5)

            # how to kill controller thread at end?
        self.disconnect.emit()

class voltageWorker(QThread):
    xVSVT = pyqtSignal(str)
    yVSVT = pyqtSignal(str)
    zVSVT = pyqtSignal(str)
    disconnect = pyqtSignal()
    xV = 0
    yV = 0
    zV = 0

    def __init__(self, serialNumber, pzhdl):
        super().__init__()
        self.serialNumber = serialNumber
        self.pzhdl = pzhdl

    def run(self):
        while (mdtIsOpen(self.serialNumber) == 1):
            mdtGetXAxisVoltage(self.pzhdl, xV)
            mdtGetYAxisVoltage(self.pzhdl, yV)
            mdtGetZAxisVoltage(self.pzhdl, zV)
            self.xVSVT.emit(str(xV))
            self.yVSVT.emit(str(yV))
            self.zVSVT.emit(str(zV))
            sleep(0.5)
        self.disconnect.emit()

if __name__ == '__main__':
    main(sys.argv)
