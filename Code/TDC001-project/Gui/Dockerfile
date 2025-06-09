FROM python:3.13-slim

# ───────── Qt & X11 deps ─────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1     libxcb-xinerama0   \
        qt6-base-dev                \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb x11vnc websockify novnc
        
WORKDIR /app
COPY v1.2-ui-chatgpt.py tdc001-ui-v1.0.0.py ./
COPY start.sh /start.sh
COPY requirements.lock .
COPY wheelhouse/ ./wheelhouse/
ARG PIP_NO_INDEX=1
RUN if [ "$PIP_NO_INDEX" = "1" ]; then \
        pip install --no-index --find-links=wheelhouse -r requirements.lock ; \
    else \
        pip install --no-cache-dir -r requirements.lock ; \
    fi

# ───────── runtime ─────────
ENV PYTHONUNBUFFERED=1

# runs the shell script to start this whole thing. 
ENTRYPOINT ["/start.sh"]
