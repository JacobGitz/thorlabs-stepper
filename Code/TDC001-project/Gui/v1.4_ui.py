"""tdc_client_ui.py — PyQt 6 GUI for Thorlabs **TDC001** cubes  (v1.5)

Classic layout • live status • steps-per‑mm presets with mm / µm conversion • LAN autodiscovery • Home ⁄ Flash ⁄ STOP
"""
from __future__ import annotations

# ── stdlib ────────────────────────────────────────────────────────────
import os, shutil, socket, subprocess, sys
from functools import partial
from typing import Dict, List, Optional

# ── third‑party ───────────────────────────────────────────────────────
import requests
from PyQt6.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFormLayout, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QStatusBar, QVBoxLayout,
    QWidget,
)
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

###############################################################################
# FastAPI REST helper (blocking, fine for GUI)
###############################################################################
class APIClient:
    def __init__(self, base: str):
        self.base = base.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base}{path if path.startswith('/') else '/' + path}"

    def _req(self, method: str, path: str, **kw):
        try:
            r = requests.request(method, self._url(path), timeout=4, **kw)
            r.raise_for_status()
            return r.json() if r.content else None
        except requests.RequestException as exc:
            raise RuntimeError(str(exc)) from exc

    list_ports = lambda s: s._req("get", "/ports")
    connect    = lambda s, port: s._req("post", "/connect", json={"port": port})
    move_rel   = lambda s, c: s._req("post", "/move_rel", json={"counts": c})
    move_abs   = lambda s, c: s._req("post", "/move_abs", json={"counts": c})
    home       = lambda s: s._req("post", "/home")
    stop       = lambda s: s._req("post", "/stop")
    flash      = lambda s: s._req("post", "/identify")

###############################################################################
# Zeroconf browser
###############################################################################
class BackendFinder(QObject):
    found = Signal(str)  # emits base‑URL

    def __init__(self):
        super().__init__()
        self.zc = Zeroconf()
        ServiceBrowser(self.zc, "_tdc001._tcp.local.", handlers=[self._on])

    def _on(self, _zc, stype, name, state):
        if state is ServiceStateChange.Added:
            info = _zc.get_service_info(stype, name)
            if info and info.addresses:
                ip = socket.inet_ntoa(info.addresses[0])
                self.found.emit(f"http://{ip}:8000")

    def close(self):
        self.zc.close()

###############################################################################
# Main GUI window
###############################################################################
class MainWindow(QMainWindow):
    STEP_PRESETS: Dict[str, Optional[int]] = {
        "T‑Cube 0.5 mm lead": 51_200,
        "T‑Cube 1.0 mm lead": 25_600,
        "Manual set…": None,
    }
    UNIT_FACT = {"mm": 1.0, "µm": 1e-3}
    _IV = QIntValidator(-1_000_000, 1_000_000)
    _FV = QDoubleValidator(0.0, 1_000.0, 4)

    def __init__(self, backend_hint: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("ThorLabs TDC001 Controller")
        self.setWindowIcon(QIcon.fromTheme("axis"))
        self.setMinimumWidth(950)

        self.api: Optional[APIClient] = None
        self.steps_per_mm: int = 51_200  # default preset

        self._build_ui()
        self._discover_backends(backend_hint)

    # ── UI layout ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        vbox = QVBoxLayout(root)

        # persistent status label
        self.lblStatus = QLabel("Status: —")
        vbox.addWidget(self.lblStatus)
        self.sb = QStatusBar(); self.setStatusBar(self.sb)

        # ── Network box
        net = QGroupBox("Network"); f = QFormLayout(net)
        self.cmbBackend = QComboBox(); self.cmbBackend.currentTextChanged.connect(self._backend_changed)
        self.cmbPort = QComboBox()
        self.btnConnect = QPushButton("Connect"); self.btnConnect.clicked.connect(self._connect)
        f.addRow("Backend:", self.cmbBackend)
        f.addRow("Cube port:", self.cmbPort)
        f.addRow("", self.btnConnect)
        vbox.addWidget(net)

        # ── Motion box
        mot = QGroupBox("Motion"); g = QGridLayout(mot)
        # preset row
        self.cmbPreset = QComboBox(); self.cmbPreset.addItems(self.STEP_PRESETS.keys()); self.cmbPreset.currentTextChanged.connect(self._preset_changed)
        self.edSteps = QLineEdit(str(self.steps_per_mm)); self.edSteps.setValidator(QIntValidator(1, 1_000_000))
        g.addWidget(QLabel("Steps/mm preset:"), 0, 0)
        g.addWidget(self.cmbPreset, 0, 1, 1, 2)
        g.addWidget(self.edSteps, 0, 3)
        # relative row
        self.edRel = QLineEdit("1.0"); self.edRel.setValidator(self._FV)
        self.cmbUnitRel = QComboBox(); self.cmbUnitRel.addItems(self.UNIT_FACT.keys())
        self.btnFwd = QPushButton("Forward (+)"); self.btnRev = QPushButton("Reverse (−)")
        self.btnFwd.clicked.connect(partial(self._move_rel, +1)); self.btnRev.clicked.connect(partial(self._move_rel, -1))
        g.addWidget(QLabel("Relative distance:"), 1, 0)
        g.addWidget(self.edRel, 1, 1)
        g.addWidget(self.cmbUnitRel, 1, 2)
        g.addWidget(self.btnFwd, 1, 3); g.addWidget(self.btnRev, 1, 4)
        # absolute row
        self.edAbs = QLineEdit("0.0"); self.edAbs.setValidator(self._FV)
        self.cmbUnitAbs = QComboBox(); self.cmbUnitAbs.addItems(self.UNIT_FACT.keys())
        self.btnGo = QPushButton("Go"); self.btnGo.clicked.connect(self._move_abs)
        g.addWidget(QLabel("Absolute pos:"), 2, 0)
        g.addWidget(self.edAbs, 2, 1)
        g.addWidget(self.cmbUnitAbs, 2, 2)
        g.addWidget(self.btnGo, 2, 3, 1, 2)
        # action row
        self.btnHome = QPushButton("Home"); self.btnHome.clicked.connect(lambda: self._safe(self.api.home))
        self.btnFlash = QPushButton("Flash LED"); self.btnFlash.clicked.connect(lambda: self._safe(self.api.flash))
        self.btnStop = QPushButton("STOP"); self.btnStop.setStyleSheet("background:#d9534f;color:white;font-weight:bold;")
        self.btnStop.clicked.connect(lambda: self._safe(self.api.stop))
        g.addWidget(self.btnHome, 3, 0, 1, 2); g.addWidget(self.btnFlash, 3, 2); g.addWidget(self.btnStop, 3, 3, 1, 2)
        vbox.addWidget(mot); vbox.addStretch()
        self._msg("Select backend…")

    # ── Back‑end discovery & selection ───────────────────────────────
    def _discover_backends(self, hint: Optional[str]):
        self.finder: Optional[BackendFinder] = None
        if hint in (None, "auto"):
            self.finder = BackendFinder(); self.finder.found.connect(self._add_backend)
        elif hint:
            self._add_backend(hint)

    @Slot(str)
    def _add_backend(self, url: str):
        if url not in (self.cmbBackend.itemText(i) for i in range(self.cmbBackend.count())):
            self.cmbBackend.addItem(url)
        if self.cmbBackend.currentIndex() == -1:
            self.cmbBackend.setCurrentIndex(0)
        self._msg(f"Discovered {url}")

    def _backend_changed(self, url: str):
        if not url:
            return
        self.api = APIClient(url)
        try:
            ports = self.api.list_ports()
        except RuntimeError as e:
            self._msg(str(e)); return
        self.cmbPort.clear(); self.cmbPort.addItems(ports)
        self._msg("Pick port and connect")

    def _connect(self):
        if not self.api:
            return
        try:
            self.api.connect(self.cmbPort.currentText())
            self._msg("Connected")
        except RuntimeError as e:
            self._msg(str(e))

    # ── Preset change ───────────────────────────────────────────────
    def _preset_changed(self, name: str):
        val = self.STEP_PRESETS[name]
        if val is None:
            self.edSteps.setEnabled(True)
        else:
            self.steps_per_mm = val
            self.edSteps.setText(str(val))
            self.edSteps.setEnabled(False)

    # ── Utility: mm / µm → counts -----------------------------------
    def _to_counts(self, dist_str: str, unit_cmb: QComboBox) -> int:
        try:
            dist = float(dist_str)
        except ValueError:
            raise ValueError("Distance invalid")
        mm = dist * self.UNIT_FACT[unit_cmb.currentText()]
        if self.edSteps.isEnabled():
            try:
                self.steps_per_mm = int(float(self.edSteps.text()))
            except ValueError:
                raise ValueError("Steps/mm invalid")
        return int(round(mm * self.steps_per_mm))

    # ── Motion handlers ---------------------------------------------
    def _move_rel(self, sign: int):
        try:
            counts = sign * abs(self._to_counts(self.edRel.text(), self.cmbUnitRel))
        except ValueError as e:
            QMessageBox.warning(self, "Invalid", str(e)); return
        self._safe(self.api.move_rel, counts)

    def _move_abs(self):
        try:
            counts = self._to_counts(self.edAbs.text(), self.cmbUnitAbs)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid", str(e)); return
        self._safe(self.api.move_abs, counts)

    # ── Safe wrapper for API calls -----------------------------------
    def _safe(self, fn, *args):
        if not self.api:
            QMessageBox.warning(self, "No backend", "Connect first"); return
        try:
            fn(*args)
            self._msg("OK")
        except RuntimeError as e:
            self._msg(str(e)); QMessageBox.critical(self, "Backend error", str(e))

    def _msg(self, msg: str):
        self.sb.showMessage(msg, 7000)
        self.lblStatus.setText(f"Status: {msg}")

###############################################################################
# Headless helper (Xvfb + websockify)                                         
###############################################################################

def _enable_novnc():
    if os.getenv("USE_NOVNC"):
        xvfb = shutil.which("Xvfb"); ws = shutil.which("websockify")
        if xvfb and ws:
            os.environ.setdefault("DISPLAY", ":99")
            subprocess.Popen([xvfb, os.environ["DISPLAY"], "-screen", "0", "1280x800x24"])
            subprocess.Popen([ws, "6080", "localhost:5900"])
        else:
            print("[WARN] USE_NOVNC requested but Xvfb/websockify not installed")

###############################################################################
# Entry‑point                                                                 
###############################################################################

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default=os.getenv("BACKEND_URL", "auto"), help="Backend URL or 'auto'")
    args = parser.parse_args()

    _enable_novnc()

    app = QApplication(sys.argv)
    window = MainWindow(backend_hint=args.backend)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

