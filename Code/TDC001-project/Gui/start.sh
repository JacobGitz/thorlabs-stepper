#!/usr/bin/env bash
set -e

if [[ "${USE_NOVNC}" == "1" ]]; then
  # --- headless path (Windows or user-forced) ---
  export DISPLAY=:99
  Xvfb       :99  -screen 0 1024x768x24  &       # virtual X
  websockify --web /usr/share/novnc/  6080  localhost:5900 &  # VNC→Web
  x11vnc  -display :99  -passwd ""  -forever  &  # VNC server
fi

# Start the PyQt GUI (same command as before)
exec python /app/v1.2-ui-chatgpt.py --url "${BACKEND_URL:-http://localhost:8000}"
