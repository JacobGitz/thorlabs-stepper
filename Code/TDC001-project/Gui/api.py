import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List

class APIClient:
    """Thin wrapper over the FastAPI‑based TDC001 backend."""
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base}/{path.lstrip('/')}"

    def _req(self, method: str, path: str, timeout: float = 3, **kwargs):
        r = self.session.request(method, self._url(path), timeout=timeout, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

    def list_ports(self) -> List[str]:
        return self._req("GET", "/ports")

    def status(self) -> dict:
        return self._req("GET", "/status")

    def connect(self, port: str):
        return self._req("POST", "/connect", json={"port": port})

    def move_rel(self, steps: int):
        return self._req("POST", "/move_rel", json={"steps": steps}, timeout=150)

    def move_abs(self, position: int):
        return self._req("POST", "/move_abs", json={"position": position}, timeout=150)

    def home(self):
        return self._req("POST", "/home", timeout=120)

    def flash(self):
        return self._req("POST", "/identify")

    def stop(self):
        return self._req("POST", "/stop")


def scan_for_backends(port: int = 8000, timeout: float = 0.25, workers: int = 64) -> List[str]:
    """
    Scans the local /24 for running backends responding to /ping.
    """
    # determine local subnet prefix
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # use a UDP connect to get our local IP
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    prefix = ".".join(local_ip.split('.')[:-1])

    def check_host(i: int) -> str:
        url = f"http://{prefix}.{i}:{port}"
        try:
            r = requests.get(f"{url}/ping", timeout=timeout)
            if r.status_code == 200:
                return url
        except requests.RequestException:
            pass
        return None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(check_host, range(1, 255))
    return [u for u in results if u]

