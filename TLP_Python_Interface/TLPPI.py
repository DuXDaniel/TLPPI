import numpy as np
import math as math
import time
import sys
from PyQt5.QtCore import QDateTime, Qt, QTimer, QObject, QThread, pyqtSignal, QRunnable
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, QDial, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar,
                             QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QHeaderView, QSpacerItem, QTableWidgetItem,
                             QTableWidgetSelectionRange, QAbstractItemView, QFileDialog, QPlainTextEdit)
from inputs import get_gamepad
import threading

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
        self.limitVoltage = [0]
        self.isMoving = 0
        self.xVoltage = [0]
        self.xV = 0 # temp set variable to prevent overwrite of array to float
        self.yVoltage = [0]
        self.yV = 0 # temp set variable to prevent overwrite of array to float
        self.zVoltage = [0]
        self.zV = 0 # temp set variable to prevent overwrite of array to float
        self.xValue = 0
        self.yValue = 0
        self.zValue = 0
        self.padStep = 0
        self.pzhdl = {}
        self.padControlToggle = 0
        self.stepArray = np.array([1, 5, 10, 25, 100, 250, 500, 1000])/65536

        super(WidgetGallery, self).__init__(parent)

        self.setMinimumSize(500, 500)
        self.setWindowTitle("ThorLabs Piezocontroller Python Interface")

        self.overallWidget()

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.fullWidget, 1, 0, 1, 1)

        self.setLayout(mainLayout)

        self.changeStyle('windowsvista')

        self.joy = XboxController(self.freeControlButton)

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

        self.yVSliderText = QLabel("Y-Axis Voltage: ")
        self.yVSliderValueText = QLabel("")
        self.yVSlider = QSlider(Qt.Horizontal)
        self.yVSlider.setFocusPolicy(Qt.StrongFocus)
        self.yVSlider.setTickPosition(QSlider.TicksBothSides)
        self.yVSlider.setTickInterval(10000)
        self.yVSlider.setSingleStep(1)
        self.yVSlider.setMinimum(0)
        self.yVSlider.setMaximum(65536)
        self.yVSlider.sliderReleased.connect(self.moveYVSlider)

        self.zVSliderText = QLabel("Z-Axis Voltage: ")
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

    def convertVoltageToVal(self, curVoltage):
        return (65536 * (curVoltage/self.limitVoltage[0]))
    
    def convertValToVoltage(self, curVal):
        return ((curVal/65536) * self.limitVoltage[0])

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
        except:
            return -1
        
        print('Hello world')
        self.serialStatus.setText(str(self.serialNumber))
        self.connectStatus.setText("On")
        self.vlimStatus.setText(str(self.limitVoltage[0]))

        mdtGetXAxisVoltage(self.pzhdl, self.xVoltage)
        mdtGetYAxisVoltage(self.pzhdl, self.yVoltage)
        mdtGetZAxisVoltage(self.pzhdl, self.zVoltage)

        self.xVSliderValueText.setText(str(self.xVoltage[0]))
        self.xValue = self.convertVoltageToVal(self.xVoltage[0])
        self.yVSliderValueText.setText(str(self.yVoltage[0]))
        self.yValue = self.convertVoltageToVal(self.yVoltage[0])
        self.zVSliderValueText.setText(str(self.zVoltage[0]))
        self.zValue = self.convertVoltageToVal(self.zVoltage[0])

        self.xVSlider.setValue(int(self.xValue))
        self.yVSlider.setValue(int(self.yValue))
        self.zVSlider.setValue(int(self.zValue))

        self.voltageStepValueText.setText(str(self.stepArray[self.padStep]))

        self.voltageTracker()
        
        self.padThread = QThread()
        self.padTracker = padWorker(self.serialNumber, self.pzhdl, self.freeControlButton, self.xVoltage, self.yVoltage, self.zVoltage, self.padStep, self.limitVoltage, self.joy, self.stepArray)
        self.padTracker.comms.connect(self.updateStatus.appendPlainText)
        self.padTracker.xVSChange.connect(self.xVSlider.setValue)
        self.padTracker.yVSChange.connect(self.yVSlider.setValue)
        self.padTracker.zVSChange.connect(self.zVSlider.setValue)
        self.padTracker.stepComms.connect(self.voltageStepValueText.setText)
        self.padTracker.moveToThread(self.padThread)
        self.padThread.started.connect(self.padTracker.run)
        self.padTracker.disconnect.connect(self.padDisconnect)
        self.padTracker.disconnect.connect(self.padThread.quit)
        self.padTracker.disconnect.connect(self.padTracker.deleteLater)
        self.padThread.finished.connect(self.padThread.deleteLater)
        
        return self.pzhdl # returns first controller found
    
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
        self.voltTracker = voltageWorker(self.serialNumber, self.pzhdl, self.xVoltage, self.yVoltage, self.zVoltage)
        self.voltTracker.xVSVT.connect(self.xVSliderValueText.setText)
        self.voltTracker.yVSVT.connect(self.yVSliderValueText.setText)
        self.voltTracker.zVSVT.connect(self.zVSliderValueText.setText)
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
            self.xVoltage[0] = self.convertValToVoltage(self.xVSlider.value())
            self.xV = self.xVoltage[0]
            mdtSetXAxisVoltage(self.pzhdl, self.xV)
            time.sleep(0.1)
            mdtGetXAxisVoltage(self.pzhdl, self.xVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def moveYVSlider(self):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.updateStatus.appendPlainText("Moving piezostage...")
            self.updateStatus.ensureCursorVisible()
            self.yVoltage[0] = self.convertValToVoltage(self.yVSlider.value())
            self.yV = self.yVoltage[0]
            mdtSetYAxisVoltage(self.pzhdl, self.yV)
            time.sleep(0.1)
            mdtGetYAxisVoltage(self.pzhdl, self.yVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def moveZVSlider(self):
        if (self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            self.updateStatus.appendPlainText("Moving piezostage...")
            self.updateStatus.ensureCursorVisible()
            self.zVoltage[0] = self.convertValToVoltage(self.zVSlider.value())
            self.zV = self.zVoltage[0]
            mdtSetZAxisVoltage(self.pzhdl, self.zV)
            time.sleep(0.1)
            mdtGetZAxisVoltage(self.pzhdl, self.zVoltage)
            self.updateStatus.appendPlainText("Movement complete.")
            self.updateStatus.ensureCursorVisible()
            time.sleep(1)

    def togglePadControl(self):
        try:
            get_gamepad()
        except:
            self.updateStatus.appendPlainText("No pad attached.")
            self.freeControlButton.setChecked(False)
            return -1

        if (self.freeControlButton.isChecked() and self.serialNumber != 0 and mdtIsOpen(self.serialNumber) == 1):
            try:
                self.joy.startThread()
                self.padThread.start()
                # update sliders on voltage change as well
                self.freeControlButton.setStyleSheet("background-color : lightblue")
                self.padControlToggle = 1
            except:
                self.updateStatus.appendPlainText("No controller attached.")
                self.freeControlButton.setStyleSheet("background-color : lightgrey")
                self.padControlToggle = 0
                self.freeControlButton.setChecked(False)
        else:
            self.freeControlButton.setStyleSheet("background-color : lightgrey")
            self.padControlToggle = 0
        
        return -1
    
    def padDisconnect(self):
        self.joy.endThread()
        self.freeControlButton.setStyleSheet("background-color : lightgrey")
        self.padControlToggle = 0
        self.padControlToggle = 0
        self.freeControlButton.setChecked(False)

class padWorker(QThread):
    comms = pyqtSignal(str)
    stepComms = pyqtSignal(str)
    disconnect = pyqtSignal()
    xVSChange = pyqtSignal(int)
    yVSChange = pyqtSignal(int)
    zVSChange = pyqtSignal(int)
    xV = 0
    yV = 0
    zV = 0
    stepx = 0
    stepy = 0
    stepz = 0
    sliderXVal = 0
    sliderYVal = 0
    sliderZVal = 0
    gamepadCheck = 0
    candidateVoltage = 0
    joyInputs = []

    def __init__(self, serialNumber, pzhdl, toggleButton, xVoltage, yVoltage, zVoltage, padStep, limitVoltage, joy, stepArray):
        super().__init__()
        self.toggleButton = toggleButton
        self.serialNumber = serialNumber
        self.pzhdl = pzhdl
        self.xVoltage = xVoltage
        self.yVoltage = yVoltage
        self.zVoltage = zVoltage
        self.padStep = padStep
        self.limitVoltage = limitVoltage
        self.joy = joy
        self.stepArray = stepArray
    
    def convertVoltageToVal(self, curVoltage):
        return (65536 * (curVoltage/self.limitVoltage[0]))
    
    def convertValToVoltage(self, curVal):
        return ((curVal/65536) * self.limitVoltage[0])
    
    def run(self):
        try:
            get_gamepad()
            self.gamepadCheck = 1
        except:
            self.gamepadCheck = 0

        while (self.toggleButton.isChecked() and self.gamepadCheck == 1):

            try:
                get_gamepad()
                self.gamepadCheck = 1
            except:
                self.gamepadCheck = 0
            
            if (self.gamepadCheck == 1):
                self.joyInputs = self.joy.read()
            else:
                self.joyInputs = [0,0,0,0,0]

            if (self.joyInputs[4] <= -0.25):
                if (self.padStep < len(self.stepArray)-1):
                    self.padStep = self.padStep + 1
                    self.stepComms.emit(str(self.stepArray[self.padStep]))
            elif (self.joyInputs[4] >= 0.25):
                if (self.padStep > 0):
                    self.padStep = self.padStep - 1
                    self.stepComms.emit(str(self.stepArray[self.padStep]))

            if (self.joyInputs[0] >= 0.25):
                self.stepx = 1
            elif (self.joyInputs[0] <= -0.25):
                self.stepx = -1
            else:
                self.stepx = 0
            
            if (self.joyInputs[1] >= 0.25):
                self.stepy = 1
            elif (self.joyInputs[1] <= -0.25):
                self.stepy = -1
            else:
                self.stepy = 0

            if (self.joyInputs[3] >= 0.25 and self.joyInputs[2] < 0.25):
                self.stepz = 1
            elif (self.joyInputs[2] >= 0.25 and self.joyInputs[3] < 0.25):
                self.stepz = -1
            else:
                self.stepz = 0

            if (self.stepx != 0):
                self.candidateVoltage = self.xVoltage[0] + self.stepx*self.stepArray[self.padStep]*self.limitVoltage[0]
                if (self.candidateVoltage > self.limitVoltage[0]):
                    self.xV = self.limitVoltage[0]
                    mdtSetXAxisVoltage(self.pzhdl,self.xV)
                elif (self.candidateVoltage < 0):
                    self.xV = 0
                    mdtSetXAxisVoltage(self.pzhdl,self.xV)
                else:
                    self.xV = self.candidateVoltage
                    mdtSetXAxisVoltage(self.pzhdl,self.xV)
            
            if (self.stepy != 0):
                self.candidateVoltage = self.yVoltage[0] + self.stepy*self.stepArray[self.padStep]*self.limitVoltage[0]
                if (self.candidateVoltage > self.limitVoltage[0]):
                    self.yV = self.limitVoltage[0]
                    mdtSetYAxisVoltage(self.pzhdl,self.yV)
                elif (self.candidateVoltage < 0):
                    self.yV = 0
                    mdtSetYAxisVoltage(self.pzhdl,self.yV)
                else:
                    self.yV = self.candidateVoltage
                    mdtSetYAxisVoltage(self.pzhdl,self.yV)

            if (self.stepz != 0):
                self.candidateVoltage = self.zVoltage[0] + self.stepz*self.stepArray[self.padStep]*self.limitVoltage[0]
                if (self.candidateVoltage > self.limitVoltage[0]):
                    self.zV = self.limitVoltage[0]
                    mdtSetZAxisVoltage(self.pzhdl,self.self.zV)
                elif (self.candidateVoltage < 0):
                    self.zV = 0
                    mdtSetZAxisVoltage(self.pzhdl,self.zV)
                else:
                    self.zV = self.candidateVoltage
                    mdtSetZAxisVoltage(self.pzhdl,self.zV)

            mdtGetXAxisVoltage(self.pzhdl, self.xVoltage)
            mdtGetYAxisVoltage(self.pzhdl, self.yVoltage)
            mdtGetZAxisVoltage(self.pzhdl, self.zVoltage)

            self.sliderXVal = int(self.convertVoltageToVal(self.xVoltage[0]))
            self.sliderYVal = int(self.convertVoltageToVal(self.yVoltage[0]))
            self.sliderZVal = int(self.convertVoltageToVal(self.zVoltage[0]))
                
            self.xVSChange.emit(self.sliderXVal)
            self.yVSChange.emit(self.sliderYVal)
            self.zVSChange.emit(self.sliderZVal)

            # how to kill controller thread at end?
        self.disconnect.emit()

class voltageWorker(QThread):
    xVSVT = pyqtSignal(str)
    yVSVT = pyqtSignal(str)
    zVSVT = pyqtSignal(str)
    disconnect = pyqtSignal()
    xV = [0]
    yV = [0]
    zV = [0]

    def __init__(self, serialNumber, pzhdl, xVoltage, yVoltage, zVoltage):
        super().__init__()
        self.serialNumber = serialNumber
        self.pzhdl = pzhdl
        self.xVoltage = xVoltage
        self.yVoltage = yVoltage
        self.zVoltage = zVoltage

    def run(self):
        while (mdtIsOpen(self.serialNumber) == 1):
            mdtGetXAxisVoltage(self.pzhdl, self.xV)
            mdtGetYAxisVoltage(self.pzhdl, self.yV)
            mdtGetZAxisVoltage(self.pzhdl, self.zV)
            self.xVoltage = self.xV
            self.yVoltage = self.yV
            self.zVoltage = self.zV
            self.xVSVT.emit(str(self.xV[0]))
            self.yVSVT.emit(str(self.yV[0]))
            self.zVSVT.emit(str(self.zV[0]))
            time.sleep(0.5)
        self.disconnect.emit()

class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
    padConnected = 0

    def __init__(self, padButton):

        self.padButton = padButton
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LRDPad = 0
        self.UDDPad = 0

    def startThread(self):
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def endThread(self):
        self._monitor_thread.join()

    def read(self): # return the buttons/triggers that you care about in this methode
        return [self.LeftJoystickX, self.LeftJoystickY, self.LeftTrigger, self.RightTrigger, self.UDDPad]

    def _monitor_controller(self):
        try:
            get_gamepad()
            self.gamepadCheck = 1
        except:
            self.gamepadCheck = 0
        
        while (self.padButton.isChecked() and self.gamepadCheck == 1):
            try:
                events = get_gamepad()
                self.gamepadCheck = 1
            except:
                self.gamepadCheck = 0

            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL # normalize between -1 and 1
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL # normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.X = event.state
                elif event.code == 'BTN_WEST':
                    self.Y = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'ABS_HAT0X':
                    self.LRDPad = event.state
                elif event.code == 'ABS_HAT0Y':
                    self.UDDPad = event.state

if __name__ == '__main__':
    main(sys.argv)
