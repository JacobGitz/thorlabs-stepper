#!/usr/bin/env python3
"""tdc_client_ui.py — PyQt6 GUI for Thorlabs TDC001 cubes (v1.5)

Live status • steps/mm presets with mm/µm conversion • LAN autodiscovery via /ping • Home/Flash/STOP
Compatible with Docker Desktop (Windows/macOS) and native Docker (Linux)
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
import socket
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Optional

import requests
from PyQt6.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class APIClient:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base}{path if path.startswith('/') else '/' + path}"

    def _req(self, method: str, path: str, **kw):
        response = requests.request(method, self._url(path), timeout=4, **kw)
        response.raise_for_status()
        return response.json() if response.content else None

    list_ports = lambda self: self._req("get", "/ports")
    connect    = lambda self, port: self._req("post", "/connect", json={"port": port})
    move_rel   = lambda self, cnt: self._req("post", "/move_rel", json={"counts": cnt})
    move_abs   = lambda self, cnt: self._req("post", "/move_abs", json={"counts": cnt})
    home       = lambda self: self._req("post", "/home")
    flash      = lambda self: self._req("post", "/identify")
    stop       = lambda self: self._req("post", "/stop")


class Worker(QObject):
    """Runs a function in a QThread and emits finished(result, error)"""
    finished = Signal(object, object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result, None)
        except Exception as e:
            self.finished.emit(None, e)


def scan_for_backends(
    port: int = 8000,
    path: str = "/ping",
    prefixes: Optional[List[str]] = None,
    timeout: float = 0.25,
    workers: int = 64,
) -> List[str]:
    """
    Scan LAN for TDC001 backends by pinging /ping endpoint.
    Includes host.docker.internal and localhost as primary targets.
    """
    # Detect local subnet
    subs: List[str] = []
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        subnet = ".".join(local_ip.split('.')[:3])
        subs.append(subnet)
    except Exception:
        pass

    # Merge default prefixes
    prefixes = prefixes or []
    for p in subs + ["192.168.0", "192.168.1", "10.0.0"]:
        if p not in prefixes:
            prefixes.append(p)

    # Build list of targets: Docker host alias, localhost, then LAN
    targets = ["host.docker.internal", "127.0.0.1"]
    for pre in prefixes:
        for i in range(1, 255):
            targets.append(f"{pre}.{i}")

    found: List[str] = []

    def try_ping(ip: str) -> Optional[str]:
        try:
            url = f"http://{ip}:{port}{path}"
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.json().get("backend") == "TDC001":
                return url
        except Exception:
            return None
        return None

    # Parallel scan
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(try_ping, targets):
            if result:
                found.append(result)
    return found


class MainWindow(QMainWindow):
    STEP_PRESETS: Dict[str, Optional[int]] = {
        "T-Cube 0.5 mm lead": 51200,
        "T-Cube 1.0 mm lead": 25600,
        "Manual set…": None,
    }
    UNIT_FACT = {"mm": 1.0, "µm": 1e-3}
    _IV = QIntValidator(-1000000, 1000000)
    _FV = QDoubleValidator(0.0, 1000.0, 4)

    def __init__(self, backend_hint: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("Thorlabs TDC001 Controller")
        self.setWindowIcon(QIcon.fromTheme("axis"))
        self.setMinimumWidth(900)

        self.api: Optional[APIClient] = None
        self.steps_per_mm = 51200

        self._build_ui()
        self._discover_backends(backend_hint)

    def _run_threaded(self, func, args=(), callback=None):
        """
        Execute func(*args) in a background QThread and invoke callback(result, error).
        """
        thread = QThread(self)
        worker = Worker(func, *args)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        if callback:
            worker.finished.connect(callback)
        # Clean up
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()

    def _build_ui(self):
        # Root layout
        root = QWidget()
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)

        # Status label + bar
        self.lblStatus = QLabel("Status: —")
        vbox.addWidget(self.lblStatus)
        self.sb = QStatusBar()
        self.setStatusBar(self.sb)

        # Network section
        net = QGroupBox("Network")
        form = QFormLayout(net)
        self.cmbBackend = QComboBox()
        self.cmbBackend.setEditable(True)
        self.cmbBackend.setPlaceholderText("http://<ip>:8000")
        self.cmbBackend.currentTextChanged.connect(self._backend_changed)

        btnAdd = QPushButton("Add")
        btnAdd.clicked.connect(self._add_manual_backend)

        self.cmbPort = QComboBox()
        btnConnect = QPushButton("Connect")
        btnConnect.clicked.connect(self._connect)

        form.addRow("Backend:", self.cmbBackend)
        form.addRow("", btnAdd)
        form.addRow("Cube port:", self.cmbPort)
        form.addRow("", btnConnect)
        vbox.addWidget(net)

        # Motion section
        mot = QGroupBox("Motion")
        grid = QGridLayout(mot)

        # Steps/mm presets
        self.cmbPreset = QComboBox()
        self.cmbPreset.addItems(self.STEP_PRESETS.keys())
        self.cmbPreset.currentTextChanged.connect(self._preset_changed)
        self.edSteps = QLineEdit(str(self.steps_per_mm))
        self.edSteps.setValidator(self._IV)
        grid.addWidget(QLabel("Steps/mm preset:"), 0, 0)
        grid.addWidget(self.cmbPreset, 0, 1, 1, 2)
        grid.addWidget(self.edSteps, 0, 3)

        # Relative move
        self.edRel = QLineEdit("1.0")
        self.edRel.setValidator(self._FV)
        self.cmbUnitRel = QComboBox()
        self.cmbUnitRel.addItems(self.UNIT_FACT.keys())
        btnFwd = QPushButton("Forward (+)")
        btnRev = QPushButton("Reverse (−)")
        btnFwd.clicked.connect(lambda: self._move_rel(+1))
        btnRev.clicked.connect(lambda: self._move_rel(-1))
        grid.addWidget(QLabel("Relative distance:"), 1, 0)
        grid.addWidget(self.edRel, 1, 1)
        grid.addWidget(self.cmbUnitRel, 1, 2)
        grid.addWidget(btnFwd, 1, 3)
        grid.addWidget(btnRev, 1, 4)

        # Absolute move
        self.edAbs = QLineEdit("0.0")
        self.edAbs.setValidator(self._FV)
        self.cmbUnitAbs = QComboBox()
        self.cmbUnitAbs.addItems(self.UNIT_FACT.keys())
        btnGo = QPushButton("Go")
        btnGo.clicked.connect(self._move_abs)
        grid.addWidget(QLabel("Absolute pos:"), 2, 0)
        grid.addWidget(self.edAbs, 2, 1)
        grid.addWidget(self.cmbUnitAbs, 2, 2)
        grid.addWidget(btnGo, 2, 3, 1, 2)

        # Action buttons
        btnHome = QPushButton("Home")
        btnFlash = QPushButton("Flash LED")
        btnStop = QPushButton("STOP")
        btnHome.clicked.connect(lambda: self._safe(self.api.home))
        btnFlash.clicked.connect(lambda: self._safe(self.api.flash))
        btnStop.setStyleSheet("background:#d9534f; color:white; font-weight:bold;")
        btnStop.clicked.connect(lambda: self._safe(self.api.stop))
        grid.addWidget(btnHome, 3, 0, 1, 2)
        grid.addWidget(btnFlash, 3, 2)
        grid.addWidget(btnStop, 3, 3, 1, 2)

        vbox.addWidget(mot)
        vbox.addStretch()

    def _discover_backends(self, hint: Optional[str]):
        # Determine initial list of candidate backend URLs
        candidates: List[str] = []
        if hint and hint != "auto":
            candidates = [hint]
        else:
            # Try detecting host IP on Linux
            try:
                host_ip = socket.gethostbyname(socket.gethostname())
                candidates.append(f"http://{host_ip}:8000")
            except Exception:
                pass
            # Always include localhost and Docker host alias
            candidates.extend([
                "http://127.0.0.1:8000",
                "http://host.docker.internal:8000",
            ])
            # Append other discovered LAN backends
            candidates += scan_for_backends()
        # Populate combo with unique URLs
        for url in dict.fromkeys(candidates):
            if url:
                self.cmbBackend.addItem(url)
        self.cmbBackend.showPopup()

    @Slot()
    def _add_manual_backend(self):
        url = self.cmbBackend.currentText().strip()
        if url and url not in [self.cmbBackend.itemText(i) for i in range(self.cmbBackend.count())]:
            self.cmbBackend.addItem(url)

    @Slot(str)
    def _backend_changed(self, url: str):
        if not url:
            return
        self.api = APIClient(url)
        self._run_threaded(self.api.list_ports, (), self._on_ports)

    def _on_ports(self, ports: Optional[List[str]], error):
        if error:
            self._msg(str(error))
            return
        self.cmbPort.clear()
        if ports:
            self.cmbPort.addItems(ports)
        self._msg("Pick port and connect")

    def _connect(self):
        if not self.api:
            return
        self._run_threaded(
            self.api.connect,
            (self.cmbPort.currentText(),),
            lambda res, err: self._msg("Connected" if not err else str(err))
        )

    def _preset_changed(self, name: str):
        val = self.STEP_PRESETS.get(name)
        self.edSteps.setEnabled(val is None)
        if val is not None:
            self.steps_per_mm = val
            self.edSteps.setText(str(val))

    def _to_counts(self, dist_str: str, unit_cmb: QComboBox) -> int:
        dist = float(dist_str)
        mm = dist * self.UNIT_FACT.get(unit_cmb.currentText(), 1.0)
        if self.edSteps.isEnabled():
            self.steps_per_mm = int(self.edSteps.text())
        return round(mm * self.steps_per_mm)

    def _move_rel(self, sign: int):
        counts = sign * abs(self._to_counts(self.edRel.text(), self.cmbUnitRel))
        self._run_threaded(
            self.api.move_rel,
            (counts,),
            lambda res, err: self._msg("OK" if not err else str(err))
        )

    def _move_abs(self):
        counts = self._to_counts(self.edAbs.text(), self.cmbUnitAbs)
        self._run_threaded(
            self.api.move_abs,
            (counts,),
            lambda res, err: self._msg("OK" if not err else str(err))
        )

    def _safe(self, fn, *args):
        self._run_threaded(
            fn,
            args,
            lambda res, err: self._msg("OK" if not err else str(err))
        )

    def _msg(self, message: str):
        self.sb.showMessage(message, 5000)
        self.lblStatus.setText(f"Status: {message}")


def _enable_novnc():
    if os.getenv("USE_NOVNC"):
        xvfb = shutil.which("Xvfb")
        ws = shutil.which("websockify")
        if xvfb and ws:
            os.environ.setdefault("DISPLAY", ":99")
            subprocess.Popen([xvfb, os.environ["DISPLAY"], "-screen", "0", "1280x800x24"])
            subprocess.Popen([ws, "6080", "localhost:5900"]);


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        default=os.getenv("BACKEND_URL", "auto"),
        help="Backend URL or 'auto'"
    )
    args = parser.parse_args()
    _enable_novnc()
    app = QApplication(sys.argv)
    window = MainWindow(backend_hint=args.backend)
    window.show()
    sys.exit(app.exec())

