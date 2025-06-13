#!/usr/bin/env python3
"""tdc_client_ui.py – PyQt6 frontend for the FastAPI‑powered **TDC001** cube

⚠ **Hotfix 2025‑06‑05** – increase network time‑outs so long
moves/homing don’t trip a *Read timed out (5 s)* error.

Key tweaks
~~~~~~~~~~
* Two distinct time‑outs:
  * **SHORT = 5 s** for quick queries like `/status`.
  * **LONG  = 120 s** for commands that can legitimately take a while
    (large moves, homing, etc.).
* `APIClient` now exposes a generic `_post_json()` that lets every high‑level
  method specify its own `timeout`.
* UI logic unchanged – just quieter now.
"""

from __future__ import annotations

# ───────── stdlib ─────────
import sys
from typing import Any, Callable, Dict, Optional

# ───────── third‑party ─────
import requests
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QMessageBox,
)

# ═════ constants ═════
SHORT = 5      # seconds (status)
LONG  = 120    # seconds (move, home, etc.)

# ═════ API helper ═════
class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    # ───── endpoints ─────
    def status(self) -> Dict[str, Any]:
        return self._get_json("/status", timeout=SHORT)

    def move_relative(self, steps: int) -> Dict[str, Any]:
        return self._post_json("/move_relative", json={"steps": steps}, timeout=LONG)

    def move_absolute(self, pos: int) -> Dict[str, Any]:
        return self._post_json("/move_absolute", json={"position": pos}, timeout=LONG)

    def home(self) -> Dict[str, Any]:
        return self._post_json("/home", timeout=LONG)

    def identify(self) -> Dict[str, Any]:
        return self._post_json("/identify", timeout=SHORT)

    def stop(self) -> Dict[str, Any]:
        return self._post_json("/stop", timeout=SHORT)

    # ───── internals ─────
    def _get_json(self, path: str, *, timeout: int) -> Dict[str, Any]:
        r = self.session.get(self.base_url + path, timeout=timeout)
        r.raise_for_status()
        return r.json()

    def _post_json(self, path: str, *, timeout: int, **kw) -> Dict[str, Any]:
        r = self.session.post(self.base_url + path, timeout=timeout, **kw)
        r.raise_for_status()
        if r.text:
            return r.json()
        return {}

# ═════ thread worker ═════
class Worker(QObject):
    done = pyqtSignal(object, object)  # (result, error)

    def __init__(self, func: Callable, *args, **kw):
        super().__init__()
        self._func, self._args, self._kw = func, args, kw

    def run(self):
        try:
            self.done.emit(self._func(*self._args, **self._kw), None)
        except Exception as e:  # noqa: BLE001
            self.done.emit(None, e)

# ═════ main window ═════
class MainWindow(QMainWindow):
    def __init__(self, api: APIClient):
        super().__init__()
        self.api = api
        self.setWindowTitle("Thorlabs TDC001 Controller")
        self._init_ui()
        self._hook_signals()
        self._poll = QTimer(self)
        self._poll.timeout.connect(self._refresh)
        self._poll.start(200)
        self._refresh()

    # ─── UI ───
    def _init_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        # status row
        self.status_lbl = QLabel("Status: —")
        self.homed_lbl  = QLabel("Homed: ?")
        self.pos_lbl    = QLabel("Pos (steps): —")
        stat = QHBoxLayout(); [stat.addWidget(w) for w in (self.status_lbl, self.homed_lbl, self.pos_lbl)]
        vbox.addLayout(stat)
        # relative controls
        rel = QHBoxLayout()
        self.steps = QSpinBox(); self.steps.setRange(-1_000_000, 1_000_000); self.steps.setValue(50000)
        self.fwd  = QPushButton("Forward (+)")
        self.rev  = QPushButton("Reverse (–)")
        rel.addWidget(QLabel("Relative (steps):")); rel.addWidget(self.steps); rel.addWidget(self.fwd); rel.addWidget(self.rev)
        vbox.addLayout(rel)
        # absolute controls
        absrow = QHBoxLayout()
        self.abs = QSpinBox(); self.abs.setRange(-2_147_483_648, 2_147_483_647)
        self.abs_go = QPushButton("Go")
        absrow.addWidget(QLabel("Absolute pos (steps):")); absrow.addWidget(self.abs); absrow.addWidget(self.abs_go)
        vbox.addLayout(absrow)
        # action row
        act = QHBoxLayout()
        self.home = QPushButton("Home")
        self.ident = QPushButton("Flash LED")
        self.stop = QPushButton("STOP"); self.stop.setStyleSheet("background:#b00;color:#fff;font-weight:bold")
        act.addWidget(self.home); act.addWidget(self.ident); act.addWidget(self.stop)
        vbox.addLayout(act)
        vbox.addStretch()

    # ─── signals ───
    def _hook_signals(self):
        self.fwd.clicked.connect(lambda: self._run(self.api.move_relative, self.steps.value()))
        self.rev.clicked.connect(lambda: self._run(self.api.move_relative, -self.steps.value()))
        self.abs_go.clicked.connect(lambda: self._run(self.api.move_absolute, self.abs.value()))
        self.home.clicked.connect(lambda: self._run(self.api.home))
        self.ident.clicked.connect(lambda: self._run(self.api.identify))
        self.stop.clicked.connect(lambda: self._run(self.api.stop))

    # ─── async runner ───
    def _run(self, fn: Callable[..., Any], *args):
        worker, thread = Worker(fn, *args), QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.done.connect(lambda res, err: self._done(thread, worker, res, err))
        thread.start()

    def _done(self, thread: QThread, worker: QObject, res: Any, err: Optional[Exception]):
        thread.quit(); thread.wait(); worker.deleteLater(); thread.deleteLater()
        if err:
            QMessageBox.critical(self, "Error", str(err))

    # ─── polling ───
    def _refresh(self):
        try:
            st = self.api.status()
        except Exception as e:
            self.status_lbl.setText(f"Status: ⚠ {e}")
            return
        self.status_lbl.setText("Status: moving" if st.get("moving_forward") or st.get("moving_reverse") else "Status: idle")
        self.homed_lbl.setText(f"Homed: {'✓' if st.get('homed') else '✗'}")
        self.pos_lbl.setText(f"Pos (steps): {st.get('position', '—')}")

    # ESC hard‑stop shortcut
    def keyPressEvent(self, ev):  # noqa: N802
        if ev.key() == Qt.Key.Key_Escape:
            self.stop.animateClick()

# ═════ entry ═════

def main(argv: Optional[list[str]] = None):
    import argparse
    p = argparse.ArgumentParser(description="PyQt6 frontend for TDC001 FastAPI backend")
    p.add_argument("--url", default="http://localhost:8000", help="Base URL (default: %(default)s)")
    args = p.parse_args(argv)
    app = QApplication(sys.argv)
    win = MainWindow(APIClient(args.url))
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

