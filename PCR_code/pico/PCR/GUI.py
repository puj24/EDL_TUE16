# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PCR_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import serial
import re
import queue
import time
import threading

class Ui_MainWindow(object):
    def __init__(self):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        self.result_queue = queue.Queue()
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True  # Set the thread as a daemon to stop it when the main thread exits
        self.serial_thread.start()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(899, 465)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(180, 20, 341, 31))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.parameters = QtWidgets.QGroupBox(self.centralwidget)
        self.parameters.setGeometry(QtCore.QRect(613, 190, 241, 121))
        self.parameters.setObjectName("parameters")
        self.layoutWidget = QtWidgets.QWidget(self.parameters)
        self.layoutWidget.setGeometry(QtCore.QRect(12, 31, 171, 77))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.Sample_T = QtWidgets.QCheckBox(self.layoutWidget)
        self.Sample_T.setObjectName("Sample_T")
        self.gridLayout.addWidget(self.Sample_T, 0, 0, 1, 1)
        self.Ideal_T = QtWidgets.QCheckBox(self.layoutWidget)
        self.Ideal_T.setObjectName("Ideal_T")
        self.gridLayout.addWidget(self.Ideal_T, 1, 0, 1, 1)
        self.Setp = QtWidgets.QCheckBox(self.layoutWidget)
        self.Setp.setObjectName("Setp")
        self.gridLayout.addWidget(self.Setp, 2, 0, 1, 1)
        self.graph = QtWidgets.QWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(30, 77, 551, 351))
        self.graph.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.graph.setObjectName("graph")
        self.time_label = QtWidgets.QLabel(self.centralwidget)
        self.time_label.setGeometry(QtCore.QRect(600, 30, 91, 21))
        self.time_label.setObjectName("time_label")
        self.progress = QtWidgets.QGroupBox(self.centralwidget)
        self.progress.setGeometry(QtCore.QRect(610, 90, 241, 91))
        self.progress.setObjectName("progress")
        self.progressBar = QtWidgets.QProgressBar(self.progress)
        self.progressBar.setGeometry(QtCore.QRect(50, 60, 151, 23))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.disp_cycle_label = QtWidgets.QLabel(self.progress)
        self.disp_cycle_label.setGeometry(QtCore.QRect(10, 30, 161, 21))
        self.disp_cycle_label.setObjectName("disp_cycle_label")
        self.show_cycle = QtWidgets.QLabel(self.progress)
        self.show_cycle.setGeometry(QtCore.QRect(170, 30, 41, 20))
        self.show_cycle.setStyleSheet("background-color: rgb(255, 255, 255);\n""border-color: rgb(213, 213, 213);")
        self.show_cycle.setObjectName("show_cycle")
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(620, 328, 241, 25))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.enter_n_label = QtWidgets.QLabel(self.layoutWidget1)
        self.enter_n_label.setObjectName("enter_n_label")
        self.gridLayout_2.addWidget(self.enter_n_label, 0, 0, 1, 1)
        self.n_cycle_inp = QtWidgets.QLineEdit(self.layoutWidget1)
        self.n_cycle_inp.setObjectName("n_cycle_inp")
        self.gridLayout_2.addWidget(self.n_cycle_inp, 0, 1, 1, 1)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(619, 361, 241, 82))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.layoutWidget2)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pause = QtWidgets.QPushButton(self.layoutWidget2)
        self.pause.setObjectName("pause")
        self.pause.clicked.connect(self.send_pause_command)
        self.gridLayout_3.addWidget(self.pause, 1, 0, 1, 1)
        self.closeb = QtWidgets.QPushButton(self.layoutWidget2)
        self.closeb.setObjectName("closeb")
        self.gridLayout_3.addWidget(self.closeb, 1, 1, 1, 1)
        self.Runpcr = QtWidgets.QPushButton(self.layoutWidget2)
        self.Runpcr.setObjectName("Runpcr")
        self.Runpcr.clicked.connect(self.send_run_pcr_command)
        self.gridLayout_3.addWidget(self.Runpcr, 0, 0, 1, 2)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(268, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 1, 0, 1, 1)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(700, 20, 151, 41))
        self.widget.setObjectName("widget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.lcd_hh = QtWidgets.QLCDNumber(self.widget)
        self.lcd_hh.setObjectName("lcd_hh")
        self.gridLayout_5.addWidget(self.lcd_hh, 0, 0, 1, 1)
        self.lcd_ss = QtWidgets.QLCDNumber(self.widget)
        self.lcd_ss.setObjectName("lcd_ss")
        self.gridLayout_5.addWidget(self.lcd_ss, 0, 2, 1, 1)
        self.lcd_mm = QtWidgets.QLCDNumber(self.widget)
        self.lcd_mm.setObjectName("lcd_mm")
        self.gridLayout_5.addWidget(self.lcd_mm, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:600;\">Pocket PCR GUI</span></p></body></html>"))
        self.parameters.setTitle(_translate("MainWindow", "Parameters"))
        self.Sample_T.setText(_translate("MainWindow", "Sample Temperature"))
        self.Ideal_T.setText(_translate("MainWindow", "Ideal Temperature"))
        self.Setp.setText(_translate("MainWindow", "Setpoint"))
        self.time_label.setText(_translate("MainWindow", "<html><head/><body><p>Time Elapsed</p></body></html>"))
        self.progress.setTitle(_translate("MainWindow", "Progress Bar"))
        self.progressBar.setWhatsThis(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.disp_cycle_label.setText(_translate("MainWindow", "No. of cycles completed"))
        self.show_cycle.setText(_translate("MainWindow", "3"))
        self.enter_n_label.setText(_translate("MainWindow", "Enter no. of cycles"))
        self.n_cycle_inp.setText(_translate("MainWindow", "36"))
        self.pause.setText(_translate("MainWindow", "Pause"))
        self.closeb.setText(_translate("MainWindow", "Close"))
        self.Runpcr.setText(_translate("MainWindow", "Run PCR"))


    def send_run_pcr_command(self):      
        try:
            ser = self.ser         
            n_cycles = int(self.n_cycle_inp.text())
            ser.write(f"{n_cycles}".encode())
            print(f"{n_cycles}".encode())
            ser.write(b"\n")

            ser.write(b"R\n")
            ser.close()
            self.__init__()
            self.read_serial()

        except Exception as e:
            print(f"Error: {e}")
    
    def send_pause_command(self):      
        try:
            ser = self.ser
            ser.write(b"P\n")
            ser.close()
            self.__init__()
        except Exception as e:
            print(f"Error: {e}")

    def read_serial(self):
        while True:
            time.sleep(0.1)
            # Read a line from the serial port
            line = self.ser.readline().decode().strip()  # Decode bytes to string and remove whitespace

            # if line:
            #     # Use regular expression to extract values
            #     match = re.match(r"Time:(.*), Ideal:(.*), Setpoint:(.*), Temperature:(.*), Duty_cycle:(.*)", line)
            #     if match:
            #         time_val = match.group(1)
            #         ideal_val = match.group(2)
            #         setpoint_val = match.group(3)
            #         temperature_val = match.group(4)
            #         duty_cycle_val = match.group(5)

            #         self.result_queue.put((time_val, ideal_val, setpoint_val, temperature_val, duty_cycle_val))
            #     # match = re.match(r"Time:(\d+):(\d+):(\d+)", time_val)
            #     # if match:
            #     #     sec_val = match.group(1)
            #     #     min_val = match.group(2)
            #     #     hrs_val = match.group(3)

            #         # self.lcd_hh.display(33)
            #         # self.lcd_mm.display(int(min_val))
            #         # self.lcd_ss.display(int(sec_val))

            #         # print("Time:",hrs_val, min_val, sec_val)
                    
            #     # Process or display the extracted values as needed
            #     # print("Time:", time_val)
            #     # print("Ideal:", ideal_val)
            #     # print("Setpoint:", setpoint_val)
            #     # print("Temperature:", temperature_val)
            #     # print("Duty Cycle:", duty_cycle_val)


if __name__ == "__main__":
    serial_port = 'COM11'
    baud_rate = 9600
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
