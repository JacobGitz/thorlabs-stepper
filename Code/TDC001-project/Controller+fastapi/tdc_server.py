#!/usr/bin/env python3
"""FastAPI wrapper for Thorlabs **TDC001** with dynamic port selection & Zeroconf."""
from __future__ import annotations

import logging, os, socket
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zeroconf import Zeroconf, ServiceInfo
from tdc001 import TDCController, find_tdc001_ports

app = FastAPI(title="TDC001 API", version="1.2.0")

log = logging.getLogger("tdc-server")
logging.basicConfig(level=logging.INFO)

controller: TDCController | None = None
zc: Zeroconf | None = None
svc: ServiceInfo | None = None

# ───────── helpers ─────────
class SelectPort(BaseModel):
    port: str

def ensure() -> TDCController:
    if controller is None:
        raise HTTPException(503, "Not connected — call /connect first")
    return controller
#  NEW bits ↓↓↓ – everything else is identical to v1.1  ──────────────────
class ConnectRequest(BaseModel):
    port: str

class MoveCounts(BaseModel):
    counts: int
    
# ───────── lifecycle ─────────
@app.on_event("startup")
def _start():
    global zc, svc
    zc = Zeroconf()
    ip = os.getenv("ADVERTISE_IP") or socket.gethostbyname(socket.gethostname())
    svc = ServiceInfo(
        "_tdc001._tcp.local.",
        f"TDCBackend-{socket.gethostname()}._tdc001._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=8000,
        properties={},
        server=f"{socket.gethostname()}.local.",
    )
    zc.register_service(svc)
    log.info("Zeroconf advertised at %s:8000", ip)

@app.on_event("shutdown")
def _stop():
    global controller, zc, svc
    if controller:
        controller.close(); controller = None
    if zc and svc:
        zc.unregister_service(svc); zc.close()

# ───────── endpoints ─────────
@app.get("/ports")
def list_ports() -> list[str]:
    return find_tdc001_ports()

@app.post("/connect")
def connect(sel: SelectPort):
    global controller
    if controller:
        controller.close()
    controller = TDCController(sel.port)
    return {"status": "connected", "port": sel.port}

@app.post("/disconnect")
def disconnect():
    global controller
    if controller:
        controller.close(); controller = None
    return {"status": "disconnected"}

@app.get("/info")
def info():
    return {"connected": controller is not None, "port": getattr(controller, "_cube", {}).serial_port if controller else None}

@app.post("/connect")
def connect(req: ConnectRequest):
    """Attach to a specific USB port chosen by the GUI."""
    global controller
    try:
        if controller:
            controller.close()
        controller = TDCController(serial_port=req.port)
        return {"status": "connected", "port": req.port}
    except Exception as e:
        controller = None
        raise HTTPException(status_code=500, detail=str(e))


# Shorter aliases expected by GUI (keep old routes too)
@app.post("/move_rel")
def move_rel(req: MoveCounts):
    return move_relative(MoveRequest(steps=req.counts))

@app.post("/move_abs")
def move_abs(req: MoveCounts):
    return move_absolute(AbsoluteRequest(position=req.counts))
    
# legacy move/home/identify/stop endpoints unchanged from v1.1 → import below
from tdc_server_legacy import *  # noqa: F401,F403 (thin wrapper to keep diff small)
