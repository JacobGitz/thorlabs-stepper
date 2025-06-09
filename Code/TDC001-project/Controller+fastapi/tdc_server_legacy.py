"""
tdc-server.py – FastAPI wrapper around TDCController

Hotfixed version (2025‑06‑04)
* Graceful startup if no cube detected
* Unified ensure_controller check → 503 Service Unavailable
* Added /stop and /ports endpoints
* Basic logging for easier debugging
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tdc001 import TDCController, find_tdc001_ports
import logging

logger = logging.getLogger("tdc-server")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="TDC001 API", version="1.1.0")

controller: TDCController | None = None


def ensure_controller() -> TDCController:
    """Return the global controller or raise 503 if no cube is attached."""
    if controller is None:
        raise HTTPException(
            status_code=503,
            detail="TDC001 device not connected. Call /ports to see available devices.",
        )
    return controller


@app.on_event("startup")
def startup_event() -> None:
    global controller
    ports = find_tdc001_ports()
    if not ports:
        logger.warning("No TDC001 cubes detected at startup – API running in degraded mode.")
        controller = None
    else:
        controller = TDCController(serial_port=ports[0])
        logger.info("Connected to TDC001 on %s", ports[0])


@app.on_event("shutdown")
def shutdown_event() -> None:
    global controller
    if controller:
        controller.close()
        logger.info("TDC001 connection closed.")


# ────────────────────────────── pydantic models ──────────────────────────────
class MoveRequest(BaseModel):
    steps: int


class AbsoluteRequest(BaseModel):
    position: int


# ──────────────────────────────── endpoints ─────────────────────────────────
@app.get("/ports")
def list_ports() -> list[str]:
    """Return serial devices that look like TDC001 cubes."""
    return find_tdc001_ports()


@app.get("/status")
def get_status():
    ctrl = ensure_controller()
    return ctrl.status


@app.post("/move_relative")
def move_relative(req: MoveRequest):
    ctrl = ensure_controller()
    try:
        ctrl.move_relative(req.steps)
        return {"status": "moved", "steps": req.steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/move_absolute")
def move_absolute(req: AbsoluteRequest):
    ctrl = ensure_controller()
    try:
        ctrl.move_absolute(req.position)
        return {"status": "moved", "position": req.position}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/home")
def home():
    ctrl = ensure_controller()
    try:
        ctrl.home()
        return {"status": "homed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/identify")
def identify():
    ctrl = ensure_controller()
    ctrl.identify()
    return {"status": "identifying"}


@app.post("/stop")
def stop():
    """Immediately stop any motion."""
    ctrl = ensure_controller()
    try:
        ctrl._cube.stop(immediate=True)
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

