# Form implementation generated from reading ui file 'revision_1.ui'
#
# Created by: PyQt6 UI code generator 6.9.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.homing_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.homing_button.setGeometry(QtCore.QRect(10, 510, 131, 41))
        self.homing_button.setObjectName("homing_button")
        self.identify_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.identify_button.setGeometry(QtCore.QRect(160, 510, 121, 41))
        self.identify_button.setObjectName("identify_button")
        self.homed_checkbox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.homed_checkbox.setGeometry(QtCore.QRect(40, 480, 92, 24))
        self.homed_checkbox.setCheckable(True)
        self.homed_checkbox.setObjectName("homed_checkbox")
        self.current_status_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_status_label.setGeometry(QtCore.QRect(10, 10, 111, 21))
        self.current_status_label.setObjectName("current_status_label")
        self.status_indicator = QtWidgets.QLabel(parent=self.centralwidget)
        self.status_indicator.setGeometry(QtCore.QRect(130, 10, 311, 21))
        self.status_indicator.setObjectName("status_indicator")
        self.forward_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.forward_button.setGeometry(QtCore.QRect(110, 200, 87, 26))
        self.forward_button.setObjectName("forward_button")
        self.reverse_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.reverse_button.setGeometry(QtCore.QRect(110, 250, 87, 26))
        self.reverse_button.setObjectName("reverse_button")
        self.relative_movement_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.relative_movement_label.setGeometry(QtCore.QRect(90, 160, 131, 16))
        self.relative_movement_label.setObjectName("relative_movement_label")
        self.step_size_entry_box = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.step_size_entry_box.setGeometry(QtCore.QRect(110, 300, 91, 31))
        self.step_size_entry_box.setObjectName("step_size_entry_box")
        self.label_stepsize = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_stepsize.setGeometry(QtCore.QRect(40, 300, 61, 31))
        self.label_stepsize.setObjectName("label_stepsize")
        self.encoder_steps_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.encoder_steps_label.setGeometry(QtCore.QRect(10, 40, 101, 21))
        self.encoder_steps_label.setObjectName("encoder_steps_label")
        self.encoder_steps_indicator = QtWidgets.QLabel(parent=self.centralwidget)
        self.encoder_steps_indicator.setGeometry(QtCore.QRect(120, 40, 121, 21))
        self.encoder_steps_indicator.setObjectName("encoder_steps_indicator")
        self.absolute_movement_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.absolute_movement_label.setGeometry(QtCore.QRect(550, 160, 141, 16))
        self.absolute_movement_label.setObjectName("absolute_movement_label")
        self.absolute_in_step_units_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.absolute_in_step_units_label.setGeometry(QtCore.QRect(470, 200, 91, 31))
        self.absolute_in_step_units_label.setObjectName("absolute_in_step_units_label")
        self.absolute_step_units_entry = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.absolute_step_units_entry.setGeometry(QtCore.QRect(560, 200, 91, 31))
        self.absolute_step_units_entry.setObjectName("absolute_step_units_entry")
        self.button_confirm_absolute = QtWidgets.QPushButton(parent=self.centralwidget)
        self.button_confirm_absolute.setGeometry(QtCore.QRect(550, 360, 87, 26))
        self.button_confirm_absolute.setObjectName("button_confirm_absolute")
        self.relative_metric_units_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.relative_metric_units_label.setGeometry(QtCore.QRect(40, 350, 71, 31))
        self.relative_metric_units_label.setObjectName("relative_metric_units_label")
        self.current_metric_indicator = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_metric_indicator.setGeometry(QtCore.QRect(130, 70, 91, 31))
        self.current_metric_indicator.setObjectName("current_metric_indicator")
        self.current_pos_metric_si_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_pos_metric_si_label.setGeometry(QtCore.QRect(230, 70, 51, 31))
        self.current_pos_metric_si_label.setObjectName("current_pos_metric_si_label")
        self.current_metric_position_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.current_metric_position_label.setGeometry(QtCore.QRect(10, 70, 111, 31))
        self.current_metric_position_label.setObjectName("current_metric_position_label")
        self.relative_metric_units_label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.relative_metric_units_label_3.setGeometry(QtCore.QRect(470, 250, 71, 31))
        self.relative_metric_units_label_3.setObjectName("relative_metric_units_label_3")
        self.absolute_metric_units_entry = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.absolute_metric_units_entry.setGeometry(QtCore.QRect(560, 250, 91, 31))
        self.absolute_metric_units_entry.setObjectName("absolute_metric_units_entry")
        self.absolute_metric_si_units_entry = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.absolute_metric_si_units_entry.setGeometry(QtCore.QRect(660, 250, 121, 31))
        self.absolute_metric_si_units_entry.setObjectName("absolute_metric_si_units_entry")
        self.relative_step_size_entry_box_metric = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.relative_step_size_entry_box_metric.setGeometry(QtCore.QRect(110, 350, 91, 31))
        self.relative_step_size_entry_box_metric.setObjectName("relative_step_size_entry_box_metric")
        self.relative_metric_si_units_entry = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.relative_metric_si_units_entry.setGeometry(QtCore.QRect(220, 350, 121, 31))
        self.relative_metric_si_units_entry.setObjectName("relative_metric_si_units_entry")
        self.cover_absolute_movement_error = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_absolute_movement_error.setGeometry(QtCore.QRect(450, 190, 341, 201))
        self.cover_absolute_movement_error.setAutoFillBackground(True)
        self.cover_absolute_movement_error.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cover_absolute_movement_error.setObjectName("cover_absolute_movement_error")
        self.cover_relative_movement_error = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_relative_movement_error.setGeometry(QtCore.QRect(110, 350, 301, 31))
        self.cover_relative_movement_error.setAutoFillBackground(True)
        self.cover_relative_movement_error.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.cover_relative_movement_error.setObjectName("cover_relative_movement_error")
        self.cover_metric_position_indicator_error = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_metric_position_indicator_error.setGeometry(QtCore.QRect(130, 70, 301, 31))
        self.cover_metric_position_indicator_error.setAutoFillBackground(True)
        self.cover_metric_position_indicator_error.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.cover_metric_position_indicator_error.setObjectName("cover_metric_position_indicator_error")
        self.cover_step_position_indicator_error = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_step_position_indicator_error.setGeometry(QtCore.QRect(120, 30, 301, 41))
        self.cover_step_position_indicator_error.setAutoFillBackground(True)
        self.cover_step_position_indicator_error.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.cover_step_position_indicator_error.setObjectName("cover_step_position_indicator_error")
        self.port_combo_box = QtWidgets.QComboBox(parent=self.centralwidget)
        self.port_combo_box.setGeometry(QtCore.QRect(680, 510, 91, 31))
        self.port_combo_box.setEditable(False)
        self.port_combo_box.setCurrentText("")
        self.port_combo_box.setObjectName("port_combo_box")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(630, 510, 41, 31))
        self.label.setObjectName("label")
        self.steps_unit_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.steps_unit_label.setGeometry(QtCore.QRect(300, 510, 81, 31))
        self.steps_unit_label.setObjectName("steps_unit_label")
        self.steps_unit_entry_box_metric = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.steps_unit_entry_box_metric.setGeometry(QtCore.QRect(380, 510, 91, 31))
        self.steps_unit_entry_box_metric.setObjectName("steps_unit_entry_box_metric")
        self.steps_unit_combo_box = QtWidgets.QComboBox(parent=self.centralwidget)
        self.steps_unit_combo_box.setGeometry(QtCore.QRect(490, 510, 91, 31))
        self.steps_unit_combo_box.setEditable(False)
        self.steps_unit_combo_box.setCurrentText("")
        self.steps_unit_combo_box.setPlaceholderText("")
        self.steps_unit_combo_box.setObjectName("steps_unit_combo_box")
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(480, 520, 16, 18))
        self.label_2.setObjectName("label_2")
        self.cover_error_no_port = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_error_no_port.setGeometry(QtCore.QRect(10, 10, 601, 551))
        self.cover_error_no_port.setAutoFillBackground(True)
        self.cover_error_no_port.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cover_error_no_port.setObjectName("cover_error_no_port")
        self.cover_error_no_port_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.cover_error_no_port_2.setGeometry(QtCore.QRect(540, 80, 251, 391))
        self.cover_error_no_port_2.setAutoFillBackground(True)
        self.cover_error_no_port_2.setText("")
        self.cover_error_no_port_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.cover_error_no_port_2.setObjectName("cover_error_no_port_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        self.menuThorlabs_TDC001_Manager = QtWidgets.QMenu(parent=self.menubar)
        self.menuThorlabs_TDC001_Manager.setObjectName("menuThorlabs_TDC001_Manager")
        self.menuDevices = QtWidgets.QMenu(parent=self.menuThorlabs_TDC001_Manager)
        self.menuDevices.setObjectName("menuDevices")
        self.menuMTS25_Z8 = QtWidgets.QMenu(parent=self.menuDevices)
        self.menuMTS25_Z8.setObjectName("menuMTS25_Z8")
        self.menuSteps_mm_2 = QtWidgets.QMenu(parent=self.menuMTS25_Z8)
        self.menuSteps_mm_2.setObjectName("menuSteps_mm_2")
        self.menuZ825B = QtWidgets.QMenu(parent=self.menuDevices)
        self.menuZ825B.setObjectName("menuZ825B")
        self.menuSteps_mm = QtWidgets.QMenu(parent=self.menuZ825B)
        self.menuSteps_mm.setObjectName("menuSteps_mm")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action34555 = QtGui.QAction(parent=MainWindow)
        self.action34555.setObjectName("action34555")
        self.action34555_2 = QtGui.QAction(parent=MainWindow)
        self.action34555_2.setObjectName("action34555_2")
        self.menuSteps_mm_2.addAction(self.action34555_2)
        self.menuMTS25_Z8.addAction(self.menuSteps_mm_2.menuAction())
        self.menuSteps_mm.addAction(self.action34555)
        self.menuZ825B.addAction(self.menuSteps_mm.menuAction())
        self.menuDevices.addAction(self.menuMTS25_Z8.menuAction())
        self.menuDevices.addAction(self.menuZ825B.menuAction())
        self.menuThorlabs_TDC001_Manager.addAction(self.menuDevices.menuAction())
        self.menubar.addAction(self.menuThorlabs_TDC001_Manager.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.homing_button.setText(_translate("MainWindow", "Home Device"))
        self.identify_button.setText(_translate("MainWindow", "Flash LED"))
        self.homed_checkbox.setText(_translate("MainWindow", "Homed"))
        self.current_status_label.setText(_translate("MainWindow", "Current Status:"))
        self.status_indicator.setText(_translate("MainWindow", "Not Moving..."))
        self.forward_button.setText(_translate("MainWindow", "Forward"))
        self.reverse_button.setText(_translate("MainWindow", "Reverse"))
        self.relative_movement_label.setText(_translate("MainWindow", "Relative Movement"))
        self.step_size_entry_box.setPlaceholderText(_translate("MainWindow", "50000"))
        self.label_stepsize.setText(_translate("MainWindow", "In Steps:"))
        self.encoder_steps_label.setText(_translate("MainWindow", "Step Position:"))
        self.encoder_steps_indicator.setText(_translate("MainWindow", "NOT_HOMED"))
        self.absolute_movement_label.setText(_translate("MainWindow", "Absolute Movement"))
        self.absolute_in_step_units_label.setText(_translate("MainWindow", "In Steps:"))
        self.absolute_step_units_entry.setPlaceholderText(_translate("MainWindow", "UNKNOWN"))
        self.button_confirm_absolute.setText(_translate("MainWindow", "Confirm"))
        self.relative_metric_units_label.setText(_translate("MainWindow", "In Metric:"))
        self.current_metric_indicator.setText(_translate("MainWindow", "UNKNOWN"))
        self.current_pos_metric_si_label.setText(_translate("MainWindow", "mm"))
        self.current_metric_position_label.setText(_translate("MainWindow", "Metric Position:"))
        self.relative_metric_units_label_3.setText(_translate("MainWindow", "In Metric:"))
        self.absolute_metric_units_entry.setPlaceholderText(_translate("MainWindow", "UNKNOWN"))
        self.absolute_metric_si_units_entry.setPlaceholderText(_translate("MainWindow", "um,mm,nm,rad"))
        self.relative_step_size_entry_box_metric.setPlaceholderText(_translate("MainWindow", "ERROR"))
        self.relative_metric_si_units_entry.setPlaceholderText(_translate("MainWindow", "um,mm,nm,rad"))
        self.cover_absolute_movement_error.setText(_translate("MainWindow", "Not Available. Must Home, Enter Steps/Unit."))
        self.cover_relative_movement_error.setText(_translate("MainWindow", "Not Available. Enter Steps/Unit."))
        self.cover_metric_position_indicator_error.setText(_translate("MainWindow", "Not Available. Must Home, Enter Steps/Unit."))
        self.cover_step_position_indicator_error.setText(_translate("MainWindow", "Not Available. Must Home."))
        self.label.setText(_translate("MainWindow", "Port:"))
        self.steps_unit_label.setText(_translate("MainWindow", "Steps/Unit:"))
        self.steps_unit_entry_box_metric.setPlaceholderText(_translate("MainWindow", "0"))
        self.label_2.setText(_translate("MainWindow", "/"))
        self.cover_error_no_port.setText(_translate("MainWindow", "Error - No Port Selected."))
        self.menuThorlabs_TDC001_Manager.setTitle(_translate("MainWindow", "Thorlabs TDC001 Manager"))
        self.menuDevices.setTitle(_translate("MainWindow", "Devices"))
        self.menuMTS25_Z8.setTitle(_translate("MainWindow", "MTS25-Z8"))
        self.menuSteps_mm_2.setTitle(_translate("MainWindow", "Steps/mm"))
        self.menuZ825B.setTitle(_translate("MainWindow", "Z825B"))
        self.menuSteps_mm.setTitle(_translate("MainWindow", "Steps/mm"))
        self.action34555.setText(_translate("MainWindow", "34555"))
        self.action34555_2.setText(_translate("MainWindow", "34555"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())

