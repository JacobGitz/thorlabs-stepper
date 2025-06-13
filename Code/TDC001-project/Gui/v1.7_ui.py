#!/usr/bin/env python3
"""tdc_client_ui.py — PyQt6 GUI for Thorlabs TDC001 cubes (v1.6)

Live status • steps/mm presets (mm/µm) • LAN scan (/ping)
Manual backend entry • Auto-populate cube ports on backend selection
Home • Flash LED • STOP • Relative & absolute moves (2 min timeout)
"""
from __future__ import annotations
import os, shutil, subprocess, sys, socket
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, List, Optional

import requests
from PyQt6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox, QLineEdit,
    QPushButton, QVBoxLayout, QFormLayout, QGroupBox,
    QGridLayout, QStatusBar, QMessageBox
)

# ─── API client with extended timeouts for moves ───────────────────
class APIClient:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base}{path if path.startswith('/') else '/' + path}"

    def _req(self, method: str, path: str, timeout: float = 3, **kw):
        r = requests.request(method, self._url(path), timeout=timeout, **kw)
        r.raise_for_status()
        return r.json() if r.content else None

    # default quick calls
    list_ports = lambda self: self._req("get",    "/ports")
    connect    = lambda self, p: self._req("post",   "/connect", json={"port": p})
    home       = lambda self: self._req("post",   "/home", timeout=120)
    flash      = lambda self: self._req("post",   "/identify")
    stop       = lambda self: self._req("post",   "/stop")
    # long‐timeout moves (120 s)
    move_rel   = lambda self, c: self._req("post",   "/move_rel",  timeout=120, json={"counts": c})
    move_abs   = lambda self, c: self._req("post",   "/move_abs",  timeout=120, json={"counts": c})


# ─── LAN scan for backends via /ping ──────────────────────────────
def scan_for_backends(port=8000, timeout=0.25, workers=64) -> List[str]:
    subnets: List[str] = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        subnets.append(".".join(ip.split('.')[:3]))
    except:
        pass

    targets = ["127.0.0.1", "host.docker.internal"]
    for p in subnets + ["192.168.0", "192.168.1", "10.0.0"]:
        targets += [f"{p}.{i}" for i in range(1,255)]

    found: List[str] = []
    def ping(h: str) -> Optional[str]:
        try:
            url = f"http://{h}:{port}/ping"
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.json().get("backend")=="TDC001":
                return f"http://{h}:{port}"
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(ping, targets):
            if res and res not in found:
                found.append(res)
    return found


# ─── Main window ─────────────────────────────────────────────────
class MainWindow(QMainWindow):
    STEP_PRESETS: Dict[str, Optional[int]] = {
        "T-Cube 0.5 mm lead": 51200,
        "T-Cube 1.0 mm lead": 25600,
        "MTS28-Z8":           34555,
        "Manual set…":        None
    }
    UNIT_FACT = {"mm": 1.0, "µm": 1e-3}

    def __init__(self, backend_hint: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("Thorlabs TDC001 Controller")
        self.setWindowIcon(QIcon.fromTheme("applications-engineering"))
        self.resize(900, 600)

        self.api: Optional[APIClient] = None
        self.steps_per_mm = 51200
        self._iv = QIntValidator(1, 1_000_000, self)
        self._dv = QDoubleValidator(0.0, 1e6, 6, self)

        self._build_ui()
        self._populate_backends(backend_hint)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)

        # Status line
        self.lblStatus = QLabel("Status: —")
        main.addWidget(self.lblStatus)
        self.sb = QStatusBar()
        self.setStatusBar(self.sb)

        # ─ Network ───────────────────────
        net = QGroupBox("Network")
        form = QFormLayout(net)

        # Backend combo + Add
        self.cmbBackend = QComboBox()
        self.cmbBackend.setEditable(True)
        self.cmbBackend.setPlaceholderText("http://<ip>:8000")
        # reload ports on select or text change
        self.cmbBackend.currentTextChanged.connect(self._load_ports)
        self.cmbBackend.currentIndexChanged.connect(
            lambda i: self._load_ports(self.cmbBackend.itemText(i))
        )
        btnAdd = QPushButton("Add")
        btnAdd.clicked.connect(lambda: self._load_ports(self.cmbBackend.currentText().strip(), add=True))

        # Port combo (auto-connect on select)
        self.cmbPort = QComboBox()
        self.cmbPort.activated.connect(lambda i: self._connect())

        form.addRow("Backend:",    self.cmbBackend)
        form.addRow("",            btnAdd)
        form.addRow("Cube port:",  self.cmbPort)

        main.addWidget(net)

        # ─ Motion ───────────────────────
        mot = QGroupBox("Motion")
        grid = QGridLayout(mot)

        # Steps/mm preset
        self.cmbPreset = QComboBox()
        self.cmbPreset.addItems(self.STEP_PRESETS.keys())
        self.cmbPreset.currentTextChanged.connect(self._on_preset)
        self.edSteps = QLineEdit(str(self.steps_per_mm))
        self.edSteps.setValidator(self._iv)
        grid.addWidget(QLabel("Steps/mm preset:"), 0, 0)
        grid.addWidget(self.cmbPreset,              0, 1, 1, 2)
        grid.addWidget(self.edSteps,                0, 3)

        # Relative move
        self.edRel    = QLineEdit("0"); self.edRel.setValidator(self._dv)
        self.cmbUnitR = QComboBox();    self.cmbUnitR.addItems(self.UNIT_FACT.keys())
        btnNeg = QPushButton("–");      btnPos = QPushButton("+")
        btnNeg.clicked.connect(partial(self._move_rel, -1))
        btnPos.clicked.connect(partial(self._move_rel, +1))
        grid.addWidget(QLabel("Move relative:"), 1, 0)
        grid.addWidget(self.edRel,             1, 1)
        grid.addWidget(self.cmbUnitR,          1, 2)
        grid.addWidget(btnNeg,                 1, 3)
        grid.addWidget(btnPos,                 1, 4)

        # Absolute move
        self.edAbs    = QLineEdit("0"); self.edAbs.setValidator(self._dv)
        self.cmbUnitA = QComboBox();    self.cmbUnitA.addItems(self.UNIT_FACT.keys())
        btnGo = QPushButton("Go to absolute"); btnGo.clicked.connect(self._move_abs)
        grid.addWidget(QLabel("Move absolute:"), 2, 0)
        grid.addWidget(self.edAbs,             2, 1)
        grid.addWidget(self.cmbUnitA,          2, 2)
        grid.addWidget(btnGo,                  2, 3, 1, 2)

        # Home / Flash / STOP
        btnHome  = QPushButton("Home");      btnHome.clicked.connect(lambda: self._safe(self.api.home))
        btnFlash = QPushButton("Flash");     btnFlash.clicked.connect(lambda: self._safe(self.api.flash))
        btnStop  = QPushButton("STOP")
        btnStop.setStyleSheet("background:#d9534f; color:white; font-weight:bold;")
        btnStop.clicked.connect(lambda: self._safe(self.api.stop))
        grid.addWidget(btnHome,   3, 0, 1, 2)
        grid.addWidget(btnFlash,  3, 2)
        grid.addWidget(btnStop,   3, 3, 1, 2)

        main.addWidget(mot)
        main.addStretch()

    def _populate_backends(self, hint: Optional[str]):
        candidates: List[str] = []
        if hint and hint != "auto":
            candidates = [hint]
        else:
            try:
                ip = socket.gethostbyname(socket.gethostname())
                candidates.append(f"http://{ip}:8000")
            except:
                pass
            candidates += ["http://127.0.0.1:8000", "http://host.docker.internal:8000"]
            candidates += scan_for_backends()

        for u in dict.fromkeys(candidates):
            if u:
                self.cmbBackend.addItem(u)

        # auto-load ports for first item
        if self.cmbBackend.count():
            self._load_ports(self.cmbBackend.currentText())

    def _load_ports(self, url: str, add: bool = False):
        url = url.strip()
        if add and url:
            seen = [self.cmbBackend.itemText(i) for i in range(self.cmbBackend.count())]
            if url not in seen:
                self.cmbBackend.addItem(url)

        if not url:
            return
        self.api = APIClient(url)
        self.sb.showMessage("Loading ports…", 2000)
        try:
            ports = self.api.list_ports()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"/ports failed:\n{e}")
            ports = []

        self.cmbPort.clear()
        self.cmbPort.addItems(ports)
        self.sb.showMessage(f"Ports: {ports}", 5000)

    def _connect(self):
        if not self.api:
            return
        port = self.cmbPort.currentText().strip()
        if not port:
            QMessageBox.warning(self, "No port", "Select a cube-port first.")
            return
        self.sb.showMessage("Connecting…", 2000)
        try:
            self.api.connect(port)
            self.sb.showMessage("Connected", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"/connect failed:\n{e}")

    def _on_preset(self, name: str):
        val = self.STEP_PRESETS[name]
        if val is None:
            self.edSteps.setReadOnly(False)
        else:
            self.edSteps.setText(str(val))
            self.edSteps.setReadOnly(True)
            self.steps_per_mm = val

    def _to_counts(self, txt: str, cmb: QComboBox) -> int:
        try:
            mm = float(txt) * self.UNIT_FACT[cmb.currentText()]
        except:
            mm = 0.0
        try:
            self.steps_per_mm = int(self.edSteps.text())
        except:
            pass
        return round(mm * self.steps_per_mm)

    def _move_rel(self, sign: int):
        cnt = sign * abs(self._to_counts(self.edRel.text(), self.cmbUnitR))
        self.sb.showMessage("Moving (relative)…", 2000)
        try:
            self.api.move_rel(cnt)
            self.sb.showMessage("Done", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"/move_rel failed:\n{e}")

    def _move_abs(self):
        cnt = self._to_counts(self.edAbs.text(), self.cmbUnitA)
        self.sb.showMessage("Moving (absolute)…", 2000)
        try:
            self.api.move_abs(cnt)
            self.sb.showMessage("Done", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"/move_abs failed:\n{e}")

    def _safe(self, fn):
        self.sb.showMessage("…", 1000)
        try:
            fn()
            self.sb.showMessage("OK", 1000)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def _enable_novnc():
    if os.getenv("USE_NOVNC"):
        xvfb = shutil.which("Xvfb")
        ws   = shutil.which("websockify")
        if xvfb and ws:
            os.environ.setdefault("DISPLAY", ":99")
            subprocess.Popen([xvfb, ":99", "-screen", "0", "1280x800x24"])
            subprocess.Popen([ws, "6080", "localhost:5900"])


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default=os.getenv("BACKEND_URL", "auto"))
    args = p.parse_args()

    _enable_novnc()
    app = QApplication(sys.argv)
    w = MainWindow(backend_hint=args.backend)
    w.show()
    sys.exit(app.exec())

