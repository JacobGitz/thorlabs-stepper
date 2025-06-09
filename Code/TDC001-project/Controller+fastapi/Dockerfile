#this is the dockerfile that sets up the backend docker container or docker image for this process
# ───────── base image ─────────
FROM python:3.13-slim

# Optional: install system libs that pyserial & thorlabs drivers may need
RUN apt-get update && apt-get install -y --no-install-recommends \
        libusb-1.0-0 dbus avahi-daemon avahi-utils \
    && rm -rf /var/lib/apt/lists/*

# ───────── copy code ─────────
WORKDIR /app
COPY tdc_server.py tdc001.py ./
COPY entrypoint.sh ./entrypoint.sh
# ───────── dependencies ──────
# If you have a 'wheelhouse' directory, copy it and force pip to use it
ARG PIP_NO_INDEX=1
COPY requirements.lock .
COPY wheelhouse/ ./wheelhouse/
RUN if [ "$PIP_NO_INDEX" = "1" ]; then \
        pip install --no-index --find-links=wheelhouse -r requirements.lock ; \
    else \
        pip install --no-cache-dir -r requirements.lock ; \
    fi

# ───────── runtime params ────
EXPOSE 8000/tcp
ENV PYTHONUNBUFFERED=1

ENTRYPOINT["/entrypoint.sh"]
