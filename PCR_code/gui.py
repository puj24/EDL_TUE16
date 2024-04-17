# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PCR_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import sys
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
# , QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber,  QSpacerItem, QSizePolicy, QProgressBar, QLineEdit, QGridLayout,QCheckBox, QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QComboBox, QGroupBox, QStatusBar
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import pyqtgraph as pg
import csv
import time
import serial

def fake_init():
    serial_port = serial.Serial('COM11', baudrate=115200, timeout=1)
    data_to_send = b"Hello, Raspberry Pi!\n"
    serial_port.write(data_to_send)
    print("Sent data:", data_to_send.decode())
    serial_port.close()

class CircularBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = np.zeros(capacity)
        self.index = 0
        self.full = False

    def push(self, value):
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.capacity
        if self.index == 0:
            self.full = True

    def get_data(self):
        if self.full:
            return np.concatenate((self.buffer[self.index:], self.buffer[:self.index]))
        else:
            return self.buffer[:self.index]


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.com_port_num = "COM11"
        self.baud_rate = 115200
        self.serial_port = QSerialPort()
        self.serial_port.setPortName(self.com_port_num)
        self.serial_port.setBaudRate(self.baud_rate)

        self.is_paused = False
        self.data_records = []

    def setupUi(self, MainWindow):
        self.setWindowTitle("Real-Time PCR Plotter")
        self.setGeometry(500, 500, 1000, 900)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1026, 580)
        self.centralwidget =QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.title = QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(210, 20, 341, 31))
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.group_name = QLabel(self.centralwidget)
        self.group_name.setGeometry(QtCore.QRect(330, 60, 81, 16))
        self.group_name.setObjectName("group_name")
        self.parameters = QGroupBox(self.centralwidget)
        self.parameters.setGeometry(QtCore.QRect(730, 180, 261, 121))
        self.parameters.setObjectName("parameters")
        self.layoutWidget = QWidget(self.parameters)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 32, 154, 77))
        self.layoutWidget.setObjectName("layoutWidget")
        self.param_grid = QGridLayout(self.layoutWidget)
        self.param_grid.setContentsMargins(0, 0, 0, 0)
        self.param_grid.setObjectName("param_grid")
        self.Sample_T = QCheckBox(self.layoutWidget)
        self.Sample_T.setObjectName("Sample_T")
        # self.Sample_T.setChecked(True)
        self.Sample_T.setStyleSheet("QCheckBox { background-color: green;  color: white; }")
        self.param_grid.addWidget(self.Sample_T, 0, 0, 1, 1)
        self.Ideal_T = QCheckBox(self.layoutWidget)
        self.Ideal_T.setObjectName("Ideal_T")
        # self.Ideal_T.setChecked(True)
        self.param_grid.addWidget(self.Ideal_T, 1, 0, 1, 1)
        self.Ideal_T.setStyleSheet("QCheckBox { background-color: red;  color: white; }")
        self.Setp = QCheckBox(self.layoutWidget)
        self.Setp.setObjectName("Setp")
        # self.Setp.setChecked(True)
        self.Setp.setStyleSheet("QCheckBox { background-color: blue;  color: white; }")
        self.param_grid.addWidget(self.Setp, 2, 0, 1, 1)
        self.graph = QWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(20, 90, 691, 441))
        self.graph.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.graph.setObjectName("graph")
        self.time_label = QLabel(self.centralwidget)
        self.time_label.setGeometry(QtCore.QRect(680, 30, 101, 21))
        self.time_label.setObjectName("time_label")
        self.progress = QGroupBox(self.centralwidget)
        self.progress.setGeometry(QtCore.QRect(730, 80, 261, 91))
        self.progress.setObjectName("progress")
        self.progressBar = QProgressBar(self.progress)
        self.progressBar.setGeometry(QtCore.QRect(30, 60, 201, 23))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.disp_cycle_label = QLabel(self.progress)
        self.disp_cycle_label.setGeometry(QtCore.QRect(20, 30, 181, 21))
        self.disp_cycle_label.setObjectName("disp_cycle_label")
        self.show_cycle = QLabel(self.progress)
        self.show_cycle.setGeometry(QtCore.QRect(200, 30, 41, 20))
        self.show_cycle.setStyleSheet("background-color: rgb(255, 255, 255);\n""border-color: rgb(213, 213, 213);")
        self.show_cycle.setObjectName("show_cycle")
        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(731, 407, 261, 46))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.n_grid = QGridLayout(self.layoutWidget1)
        self.n_grid.setContentsMargins(0, 0, 0, 0)
        self.n_grid.setObjectName("n_grid")
        self.enter_n_label = QLabel(self.layoutWidget1)
        self.enter_n_label.setObjectName("enter_n_label")
        self.n_grid.addWidget(self.enter_n_label, 0, 0, 1, 1)
        self.n_cycle_inp = QLineEdit(self.layoutWidget1)
        self.n_cycle_inp.setObjectName("n_cycle_inp")
        self.n_cycle_inp.setMaxLength(2)
        self.n_grid.addWidget(self.n_cycle_inp, 0, 1, 1, 1)
        self.layoutWidget2 = QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(730, 470, 261, 82))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.gridLayout_4 = QGridLayout(self.layoutWidget2)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pause = QPushButton(self.layoutWidget2)
        self.pause.setObjectName("pause")
        self.pause.clicked.connect(self.on_pause_clicked)
        self.gridLayout_3.addWidget(self.pause, 1, 0, 1, 1)
        self.export = QPushButton(self.layoutWidget2)
        self.export.setObjectName("export")
        self.gridLayout_3.addWidget(self.export, 1, 1, 1, 1)
        self.Runpcr = QPushButton(self.layoutWidget2)
        self.Runpcr.setObjectName("Runpcr")
        self.Runpcr.clicked.connect(self.send_run_pcr_command)
        self.gridLayout_3.addWidget(self.Runpcr, 0, 0, 1, 2)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem = QSpacerItem(268, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 1, 0, 1, 1)
        self.widget = QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(790, 20, 206, 41))
        self.widget.setObjectName("widget")
        self.time_grid = QGridLayout(self.widget)
        self.time_grid.setContentsMargins(0, 0, 0, 0)
        self.time_grid.setObjectName("time_grid")
        self.lcd_hh = QLCDNumber(self.widget)
        self.lcd_hh.setObjectName("lcd_hh")
        self.time_grid.addWidget(self.lcd_hh, 0, 0, 1, 1)
        self.lcd_ss = QLCDNumber(self.widget)
        self.lcd_ss.setObjectName("lcd_ss")
        self.time_grid.addWidget(self.lcd_ss, 0, 2, 1, 1)
        self.lcd_mm = QLCDNumber(self.widget)
        self.lcd_mm.setObjectName("lcd_mm")
        self.time_grid.addWidget(self.lcd_mm, 0, 1, 1, 1)
        color = QColor(255, 245, 245) 
        self.change_text_color(self.lcd_hh, color)
        self.change_text_color(self.lcd_mm, color)
        self.change_text_color(self.lcd_ss, color)

        
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(730, 310, 261, 91))
        self.groupBox.setObjectName("groupBox")
        self.widget1 = QWidget(self.groupBox)
        self.widget1.setGeometry(QtCore.QRect(10, 30, 251, 51))
        self.widget1.setObjectName("widget1")
        self.gridLayout = QGridLayout(self.widget1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.COM_PORT = QLabel(self.widget1)
        self.COM_PORT.setObjectName("COM_PORT")
        self.gridLayout.addWidget(self.COM_PORT, 0, 0, 1, 1)
        self.enter_com = QLineEdit(self.widget1)
        self.enter_com.setAlignment(QtCore.Qt.AlignCenter)
        self.enter_com.setObjectName("enter_com")
        self.gridLayout.addWidget(self.enter_com, 0, 1, 1, 1)
        self.BAUDRATE = QLabel(self.widget1)
        self.BAUDRATE.setObjectName("BAUDRATE")
        self.gridLayout.addWidget(self.BAUDRATE, 1, 0, 1, 1)
        self.enter_baud = QLineEdit(self.widget1)
        self.enter_baud.setAlignment(QtCore.Qt.AlignCenter)
        self.enter_baud.setObjectName("enter_baud")
        self.gridLayout.addWidget(self.enter_baud, 1, 1, 1, 1)

        self.madeby = QLabel(self.centralwidget)
        self.madeby.setGeometry(QtCore.QRect(300, 540, 91, 16))
        self.madeby.setObjectName("madeby")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.graph = pg.PlotWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(20, 90, 691, 441))
        self.graph.showGrid(True, True)
        self.graph.setLabel("left", "Temperature")
        self.graph.setLabel("bottom", "Time")
        self.graph.setMouseEnabled(x=True, y=False)
        self.graph.setClipToView(True)
        self.graph.setXRange(0,500)
        self.graph.setYRange(10,100)  

        self.sensor_data = {}
        self.time_values = []

        self.buffer_sizes = [1000, 3000, 100000, 7000, 10000]
        self.buffer_capacity = self.buffer_sizes[2]


        self.export.clicked.connect(self.export_data)
        self.export.setEnabled(False)
        self.pause.setEnabled(False)

        self.prev_temperature = None
        self.prev_setpoint = 95.5
        self.progress_perc = 0
        self.N_cycles_completed = 0
        self.N_cycles_given = 0

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Real Time PCR Plotter"))
        self.title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:600;\">Pocket PCR GUI</span></p></body></html>"))
        self.group_name.setText(_translate("MainWindow", "EDL-TUE-16"))
        self.parameters.setTitle(_translate("MainWindow", "Parameters"))
        self.Sample_T.setText(_translate("MainWindow", "Sample Temperature"))
        self.Ideal_T.setText(_translate("MainWindow", "Ideal Temperature"))
        self.Setp.setText(_translate("MainWindow", "Setpoint"))
        self.time_label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:9pt;\">Time Elapsed</span></p></body></html>"))
        self.progress.setTitle(_translate("MainWindow", "Progress Bar"))
        self.progressBar.setWhatsThis(_translate("MainWindow", "<html><head/><body><p><br/></p></body></html>"))
        self.disp_cycle_label.setText(_translate("MainWindow", "No. of cycles completed"))
        self.show_cycle.setText(_translate("MainWindow", "0"))
        self.enter_n_label.setText(_translate("MainWindow", "Enter no. of cycles"))
        self.n_cycle_inp.setText(_translate("MainWindow", "1"))
        self.pause.setText(_translate("MainWindow", "Pause"))
        self.export.setText(_translate("MainWindow", "Export"))
        self.Runpcr.setText(_translate("MainWindow", "Run PCR"))
        self.groupBox.setTitle(_translate("MainWindow", "Serial port"))
        self.COM_PORT.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:8pt;\">COM PORT</span></p></body></html>"))
        self.enter_com.setText(_translate("MainWindow", "COM11"))
        self.BAUDRATE.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:8pt;\">BAUD RATE</span></p></body></html>"))
        self.enter_baud.setText(_translate("MainWindow", "115200"))
        self.madeby.setText(_translate("MainWindow", "Made by PNP"))


    def change_text_color(self, lcd_widget, color):
        palette = lcd_widget.palette()
        palette.setColor(palette.Text, color)
        lcd_widget.setPalette(palette)
        # lcd_widget.setSegmentStyle(QLCDNumber.Flat)
        lcd_widget.setDigitCount(2) 

    def send_run_pcr_command(self): 
        self.N_cycles_given = self.n_cycle_inp.text()
        print(self.N_cycles_given)
        bytes_to_write = self.N_cycles_given.encode('utf-8')
        self.serial_port.write(bytes_to_write)
        self.serial_port.write(b'\nR')
        self.pause.setEnabled(True)
        self.serial_port.readyRead.connect(self.receive_serial_data)


    def add_sensor(self, name, color):
        self.sensor_data[name] = {
            'buffer': CircularBuffer(self.buffer_capacity),
            'plot_item': self.graph.plot(pen=pg.mkPen(color, width=2), name=name),
        }

    def change_buffer_size(self, index):
        self.buffer_capacity = self.buffer_sizes[index]
        for sensor in self.sensor_data.values():
            sensor['buffer'] = CircularBuffer(self.buffer_capacity)

    def on_pause_clicked(self, MainWindow):
        self.pause_updates()
        _translate = QtCore.QCoreApplication.translate
        if self.is_paused:
            self.pause.setText(_translate("MainWindow", "Resume"))
            self.export.setEnabled(True)
        else:
            self.pause.setText(_translate("MainWindow", "Pause"))
            self.export.setEnabled(False)

    def pause_updates(self):
        self.is_paused = not self.is_paused

    def resume_updates(self):
        self.is_paused = False      

    def export_data(self):
        if len(self.data_records) > 0:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "", "CSV Files (*.csv)")
            if filename:
                try:
                    with open(filename, "w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(["Sensor", "Value"])
                        writer.writerows(self.data_records)
                    QMessageBox.information(
                        self, "Export Success", "Data exported successfully.")
                except Exception as e:
                    QMessageBox.warning(
                        self, "Export Error", f"Failed to export data: {str(e)}")
            else:
                QMessageBox.warning(self, "Export Error", "Invalid filename.")
        else:
            QMessageBox.warning(self, "Export Error", "No data to export.")

    def receive_serial_data(self):
        # print("receiving data")
        while self.serial_port.canReadLine():
            try:
                data = self.serial_port.readLine().data().decode("utf-8").strip()
                print(data)
                values = data.split(",")
                for value in values:
                    sensor_data = value.split(":")
                    sensor_name = sensor_data[0].strip()
                    sensor_value = float(sensor_data[1].strip())
                    if sensor_name== "Time":
                        self.time_values.append(sensor_value)
                        sec = int(sensor_value)
                        min = sec//60
                        hrs = min/60
                        self.lcd_ss.display(sec%60)
                        self.lcd_mm.display(int(min%60))
                        self.lcd_hh.display(hrs)
                        # self.progressBar.setValue(int(sec/4))
                    elif sensor_name == "N_cy_comp":
                        self.N_cycles_completed = int(sensor_value)
                        self.show_cycle.setText(str(self.N_cycles_completed))
                    if sensor_name in self.sensor_data and not self.is_paused:
                        if(sensor_name == "Temperature"):
                            current_temp = sensor_value
                            if self.prev_temperature is not None and abs(current_temp - self.prev_temperature) > 1.5:
                                current_temp = self.prev_temperature  # Keep the previous temperature
                            self.prev_temperature = current_temp
                            sensor_value = current_temp
                            
                        elif(sensor_name == "Setpoint"):
                            current_setp = sensor_value
                            if(current_setp != self.prev_setpoint):
                                self.progress_perc += 33.3* self.N_cycles_completed/int(self.N_cycles_given)
                                self.progressBar.setValue(int(self.progress_perc))
                        
                        data_buffer = self.sensor_data[sensor_name]['buffer']
                        data_buffer.push(sensor_value)
                        self.sensor_data[sensor_name]['plot_item'].setData(self.time_values, data_buffer.get_data())
                        self.data_records.append([sensor_name, sensor_value])
            except (UnicodeDecodeError, IndexError, ValueError):
                pass


if __name__ == "__main__":
    fake_init()
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.add_sensor("Ideal", 'r')
    ui.add_sensor("Setpoint", 'b')
    ui.add_sensor("Temperature", 'g')
    ui.add_sensor("Duty_Cycle", 'y')

    if ui.serial_port.open(QSerialPort.ReadWrite):
        MainWindow.show()
        sys.exit(app.exec_())
    else:
        print("Failed to open serial port.")
        sys.exit(1)

