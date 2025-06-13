#!/usr/bin/env python3
"""
Main Window Module

This module defines the MainWindow class, which provides a PyQt6 graphical user interface
for controlling a Thorlabs TDC001 device over a networked backend. It is a modular refactoring
of the v1.8 UI, with an added "Homed" indicator from v1.1.

Key features:
- Status, Homed, and Position display
- Backend discovery and manual entry
- Cube-port selection and auto-restore of saved position
- Steps/mm presets and editable conversion factor
- Relative and absolute move controls
- Home, Flash, and STOP commands via threaded tasks
- Persistent saving of last-known positions
"""

import sys  # system-specific parameters and functions
import os
import datetime  # date and time handling
import socket  # network interface discovery
import shutil  # shell utilities
import subprocess  # launching subprocesses

from functools import partial  # helper for partial function application
from concurrent.futures import ThreadPoolExecutor  # thread pool for scanning

import requests  # HTTP requests to backend

# PyQt6 GUI imports: core widgets, layouts, dialogs, and validators
from PyQt6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QFormLayout,
    QGroupBox, QStatusBar, QMessageBox
)
from PyQt6.QtCore import QTimer, QThread  # timers and threading support

# Application-specific modules: API client, constants, storage, and worker
from api import APIClient, scan_for_backends
from constants import STEP_PRESETS, UNIT_FACT
from storage import load_positions, save_positions
from task_runner import Worker


class MainWindow(QMainWindow):
    """
    MainWindow

    A QMainWindow subclass that sets up the main user interface for the TDC001 controller.
    It loads saved positions, discovers backends, and starts a periodic status poll.
    """
    def __init__(self, backend_hint=None):
        super().__init__()  # initialize QMainWindow base class
        # Window configuration
        self.setWindowTitle("Thorlabs TDC001 Controller")  # window title
        self.setWindowIcon(QIcon.fromTheme("applications-engineering"))  # window icon
        self.resize(900, 600)  # initial window size

        # ----- Persistent state variables -----
        self.api = None  # will hold APIClient instance
        # default steps/mm from presets or fallback to 1
        self.steps_per_mm = STEP_PRESETS.get('T-Cube 0.5 mm lead') or 1
        self.positions = load_positions()  # load saved positions from disk
        self.homed = False  # track whether device is considered homed

        # ----- Input validators -----
        self.int_val = QIntValidator(1, 10**6, self)  # for integer-only fields
        self.fl_val = QDoubleValidator(0.0, 1e6, 6, self)  # for floating-point fields

        # Build UI components and start status polling
        self._build_ui()  # sets up widgets and layouts
        self._discover_backends(backend_hint)  # populate backend list
        self.timer = QTimer(self)  # create a QTimer for periodic updates
        self.timer.timeout.connect(self._refresh_status)  # connect to status refresh
        self.timer.start(500)  # fire every 500 ms

    def _build_ui(self):
        """
        Build UI

        Creates all widgets, layouts, and signal-slot connections.
        Organizes them into logical groups: status, network, motion, and control.
        """
        # Central widget and main vertical layout
        central = QWidget(self)
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)  # top-level vertical layout
        main_v.setSpacing(10)  # spacing between sections
        main_v.setContentsMargins(10, 10, 10, 10)  # outer margins

        # --- Status Row: three labels in a horizontal layout ---
        status_h = QHBoxLayout()
        self.lbl_status = QLabel("Status: —")  # shows idle/moving
        self.lbl_homed = QLabel("Homed: ✗")  # shows homed state
        self.lbl_pos = QLabel("Pos: — cnt | — mm")  # shows encoder counts & mm
        for w in (self.lbl_status, self.lbl_homed, self.lbl_pos):
            status_h.addWidget(w)  # add each label to the row
        status_h.addStretch()  # push labels to the left
        main_v.addLayout(status_h)  # insert into main layout

        # --- Network Group: backend & cube-port selection ---
        net_grp = QGroupBox("Network")  # group box container
        net_form = QFormLayout(net_grp)  # form layout for labels + fields
        # Backend URL dropdown, editable
        self.cmb_backend = QComboBox()
        self.cmb_backend.setEditable(True)
        self.cmb_backend.setPlaceholderText("http://<ip>:8000")
        self.cmb_backend.currentTextChanged.connect(self._on_backend_change)
        # Button to save a manually entered backend URL
        btn_add = QPushButton("Add Backend")
        btn_add.clicked.connect(self._add_backend)
        # Cube-port dropdown (e.g., /dev/ttyUSB0)
        self.cmb_port = QComboBox()
        self.cmb_port.currentIndexChanged.connect(self._connect_device)
        # assemble form rows
        net_form.addRow("Backend:", self.cmb_backend)
        net_form.addRow("", btn_add)
        net_form.addRow("Cube port:", self.cmb_port)
        main_v.addWidget(net_grp)

        # --- Motion Group: presets & move controls ---
        mot_grp = QGroupBox("Motion")
        grid = QGridLayout(mot_grp)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(4)
        # Steps/mm preset dropdown + editable field
        grid.addWidget(QLabel("Steps/mm preset:"), 0, 0)
        self.cmb_preset = QComboBox()
        self.cmb_preset.addItems(STEP_PRESETS.keys())
        self.cmb_preset.currentTextChanged.connect(self._on_preset)
        grid.addWidget(self.cmb_preset, 0, 1)
        self.ed_steps = QLineEdit(str(self.steps_per_mm))
        self.ed_steps.setValidator(self.int_val)
        grid.addWidget(self.ed_steps, 0, 2)
        # Relative move: distance + unit + buttons
        grid.addWidget(QLabel("Move relative:"), 1, 0)
        self.ed_rel = QLineEdit("0")
        self.ed_rel.setValidator(self.fl_val)
        grid.addWidget(self.ed_rel, 1, 1)
        self.cmb_unit_rel = QComboBox()
        self.cmb_unit_rel.addItems(UNIT_FACT.keys())
        grid.addWidget(self.cmb_unit_rel, 1, 2)
        btn_neg = QPushButton("–")
        btn_neg.clicked.connect(lambda: self._move_rel(-1))
        btn_pos = QPushButton("+")
        btn_pos.clicked.connect(lambda: self._move_rel(1))
        grid.addWidget(btn_neg, 1, 3)
        grid.addWidget(btn_pos, 1, 4)
        # Absolute move: distance + unit + go button
        grid.addWidget(QLabel("Move absolute:"), 2, 0)
        self.ed_abs = QLineEdit("0")
        self.ed_abs.setValidator(self.fl_val)
        grid.addWidget(self.ed_abs, 2, 1)
        self.cmb_unit_abs = QComboBox()
        self.cmb_unit_abs.addItems(UNIT_FACT.keys())
        grid.addWidget(self.cmb_unit_abs, 2, 2)
        btn_go = QPushButton("Go to absolute")
        btn_go.clicked.connect(self._move_abs)
        grid.addWidget(btn_go, 2, 3, 1, 2)
        # Control buttons: Home, Flash, STOP
        btn_home = QPushButton("Home")
        btn_home.clicked.connect(lambda: self._run_async(self.api.home))
        btn_flash = QPushButton("Flash")
        btn_flash.clicked.connect(lambda: self._run_async(self.api.flash))
        btn_stop = QPushButton("STOP")
        btn_stop.setStyleSheet("background:#d9534f;color:white;font-weight:bold;")
        btn_stop.clicked.connect(lambda: self._run_async(self.api.stop))
        grid.addWidget(btn_home, 3, 0)
        grid.addWidget(btn_flash, 3, 1)
        grid.addWidget(btn_stop, 3, 2, 1, 3)
        main_v.addWidget(mot_grp)

        # Add stretch at bottom to prevent large empty gaps
        main_v.addStretch()

        # Bottom status bar for transient messages
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def _discover_backends(self, hint=None):
        """
        Discover Backends

        Populates the backend dropdown with:
        - A manual hint if provided
        - Common localhost URLs
        - Automatically scans the LAN for /ping responses
        """
        candidates = []  # list of URLs
        if hint and hint != 'auto':
            candidates.append(hint)
        else:
            candidates += ['http://127.0.0.1:8000', 'http://host.docker.internal:8000']
            try:
                # discover local IP address
                ip = socket.gethostbyname(socket.gethostname())
                candidates.append(f"http://{ip}:8000")
            except:
                pass
            # LAN scan in parallel
            candidates += scan_for_backends()
        # add unique URLs to combo box
        for url in dict.fromkeys(candidates):
            self.cmb_backend.addItem(url)
        if self.cmb_backend.count():
            # trigger initial port load
            self._on_backend_change(self.cmb_backend.currentText())

    def _add_backend(self):
        """
        Add Backend

        Saves the currently typed backend URL into the dropdown list, if new.
        """
        url = self.cmb_backend.currentText().strip()
        if url and self.cmb_backend.findText(url) == -1:
            self.cmb_backend.addItem(url)
            self.cmb_backend.setCurrentText(url)

    def _on_backend_change(self, url):
        """
        Backend Changed

        Called when the user selects or edits the backend URL.
        Connects to that URL and requests the list of cube ports.
        """
        if not url:
            return
        self.api = APIClient(url)  # new API client instance
        self.statusbar.showMessage("Loading ports...", 2000)
        try:
            ports = self.api.list_ports()
        except Exception as e:
            # show error dialog on failure
            QMessageBox.critical(self, "Error", f"/ports failed:\n{e}")
            ports = []
        # update cube-port dropdown
        self.cmb_port.clear()
        self.cmb_port.addItems(ports)
        self.statusbar.showMessage(f"Ports: {ports}", 2000)

    def _connect_device(self):
        """
        Connect Device

        Called when the user selects a cube-port. Connects to the TDC001 device,
        optionally restores last saved position, and marks the device as homed.
        """
        port = self.cmb_port.currentText().strip()
        if not port:
            QMessageBox.warning(self, "No port", "Select a cube-port first.")
            return
        key = f"{self.api.base}|{port}"  # unique key per backend+port
        last = self.positions.get(key)
        if last:
            # ask user to restore previous position
            msg = f"Previous pos: {last['pos']} cnt ({last['pos']/self.steps_per_mm:.3f} mm) @ {last['time']}. Restore?"
            if QMessageBox.question(self, "Restore", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.homed = True
                mm = last['pos'] / self.steps_per_mm
                self.ed_abs.setText(f"{mm:.3f}")  # update absolute field
                self.lbl_pos.setText(f"Pos: {last['pos']} cnt | {mm:.3f} mm")
        try:
            self.api.connect(port)  # instruct backend to connect
            self.statusbar.showMessage("Connected", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"/connect failed:\n{e}")

    def _on_preset(self, name):
        """
        Preset Changed

        When the user selects a steps/mm preset, set or unlock the steps field.
        """
        val = STEP_PRESETS.get(name)
        if val is None:
            self.ed_steps.setReadOnly(False)  # allow manual entry
        else:
            self.steps_per_mm = val  # update conversion factor
            self.ed_steps.setText(str(val))
            self.ed_steps.setReadOnly(True)

    def _to_counts(self, txt, cmb):
        # convert a text distance + unit combo into encoder counts
        try:
            dist = float(txt) * UNIT_FACT[cmb.currentText()]
        except:
            dist = 0.0
        try:
            self.steps_per_mm = int(self.ed_steps.text())
        except:
            pass
        return round(dist * self.steps_per_mm)

    def _move_rel(self, sign):
        """
        Move Relative

        Moves the device by the specified signed distance (±), in a background thread.
        """
        cnt = sign * abs(self._to_counts(self.ed_rel.text(), self.cmb_unit_rel))
        self.statusbar.showMessage("Moving relative...", 2000)
        self._run_async(self.api.move_rel, cnt)  # start threaded move

    def _move_abs(self):
        """
        Move Absolute

        Moves the device to the specified absolute position, in a background thread.
        """
        cnt = self._to_counts(self.ed_abs.text(), self.cmb_unit_abs)
        self.statusbar.showMessage("Moving absolute...", 2000)
        self._run_async(self.api.move_abs, cnt)

    def _refresh_status(self):
        """
        Refresh Status

        Called periodically by QTimer to query backend status.
        Updates status label, homed indicator, position, and saves state.
        """
        if not self.api:
            self.lbl_status.setText("Status: no backend")
            self.lbl_homed.setText("Homed: ✗")
            return
        try:
            st = self.api.status()  # fetch JSON status
        except Exception as e:
            self.lbl_status.setText(f"Status: ⚠ {e}")
            return
        # determine movement and homed state
        busy = st.get('moving_forward') or st.get('moving_reverse')
        homed_flag = st.get('homed', False)
        # update labels
        self.lbl_status.setText("Status: moving" if busy else "Status: idle")
        self.lbl_homed.setText(f"Homed: {'✓' if homed_flag else '✗'}")
        pos = st.get('position', 0)
        mm = pos / self.steps_per_mm
        self.lbl_pos.setText(f"Pos: {pos} cnt | {mm:.3f} mm")
        # save position if homed and idle
        if homed_flag and not busy:
            port = self.cmb_port.currentText().strip()
            key = f"{self.api.base}|{port}"
            self.positions[key] = {'pos': pos, 'time': datetime.datetime.now().isoformat()}
            save_positions(self.positions)

    def _run_async(self, fn, *args):
        """
        Run Async Task

        Wraps backend calls in a Worker/QThread for non-blocking GUI.
        """
        if not callable(fn):
            return
        worker = Worker(fn, *args)  # create worker for function
        thread = QThread(self)  # new thread for this task
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(lambda res, err: self._on_done(thread, worker, res, err))
        thread.start()  # start background thread

    def _on_done(self, thread, worker, res, err):
        """
        Task Finished

        Handles cleanup after Worker completes, shows errors or OK.
        """
        thread.quit()
        thread.wait()
        worker.deleteLater()
        thread.deleteLater()
        if err:
            QMessageBox.critical(self, "Error", str(err))
        else:
            self.statusbar.showMessage("Done", 2000)
            self._refresh_status()


if __name__ == "__main__":
    from run import main  # import launcher
    main()  # start application

