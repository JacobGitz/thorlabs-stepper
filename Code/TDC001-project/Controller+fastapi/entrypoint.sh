#!/usr/bin/env bash
set -e

# 1) start dbus & avahi so zeroconf works
dbus-daemon --system --fork
avahi-daemon --daemonize

# advertise ourselves on the LAN
avahi-publish-service tdc001 _tdc001._tcp 8000 &

# 2) launch FastAPI
exec uvicorn tdc_server:app --host 0.0.0.0 --port 8000
