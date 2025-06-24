#!/usr/bin/env bash
#
# Thorlabs TDC001 backend one-click launcher
# • builds / pulls the “backend” service from docker-compose.backend.yml
# • starts (or restarts) the container
# • opens http://localhost:8000/docs (FastAPI swagger)
# • optionally plants a desktop shortcut
#

################### configuration ########################################
compose_relative="../Code/TDC001-project/docker-compose.backend.yml"
service="tdc_backend" # docker-compose service name
port=8000             # FastAPI external port
shortcut_name="TDC001 Backend.desktop"
icon_path="$(dirname "$0")/tdc_backend.png" # optional .png next to this script
##########################################################################

echo -e "\n\e[36m──────── Thorlabs TDC001 BACKEND launcher ────────\e[0m\n"

# 1) locate compose file -------------------------------------------------
script_dir="$(cd -- "$(dirname "$0")" && pwd)"
compose_file="$(realpath "$script_dir/$compose_relative")"

if [[ ! -f "$compose_file" ]]; then
  echo -e "\e[31m[ERROR]\e[0m Compose file not found: $compose_file"
  read -rp "Press Enter to exit…" _
  exit 1
fi
echo "[INFO] Compose file  $compose_file"

# 2) docker available? ---------------------------------------------------
if ! command -v docker &>/dev/null; then
  echo -e "\e[31m[ERROR]\e[0m Docker CLI not found."
  read -rp "Press Enter to exit…" _
  exit 1
fi
if ! docker info &>/dev/null; then
  echo -e "\e[31m[ERROR]\e[0m Docker daemon is not running."
  read -rp "Press Enter to exit…" _
  exit 1
fi

# 3) pull / build & start service ---------------------------------------
echo "[INFO] (re)creating container…"
docker compose -f "$compose_file" up --build -d "$service"
if [[ $? -ne 0 ]]; then
  echo -e "\e[31m[ERROR]\e[0m docker compose failed."
  read -rp "Press Enter to exit…" _
  exit 1
fi

# 4) wait for FastAPI ----------------------------------------------------
printf "[INFO] Waiting for backend on localhost:%d" "$port"
for _ in {1..30}; do
  if curl -s "http://localhost:$port/ping" &>/dev/null; then
    echo " – ready!"
    break
  fi
  printf "."
  sleep 0.5
done

# 5) open browser --------------------------------------------------------
echo "[INFO] Opening browser…"
xdg-open "http://localhost:$port/docs" &>/dev/null &

# 6) desktop shortcut (ask once) ----------------------------------------
desk="$HOME/Desktop"
link="$desk/$shortcut_name"
if [[ ! -e "$link" && -d "$desk" ]]; then
  read -p "Create a desktop shortcut for the backend? [y/N] " ans
  if [[ ${ans,,} == y* ]]; then
    cat >"$link" <<EOF
[Desktop Entry]
Type=Application
Name=Thorlabs TDC001 Backend
Comment=Start the TDC001 API server
Exec=$(realpath "$0")
Icon=${icon_path:-utilities-terminal}
Terminal=true
EOF
    chmod +x "$link"
    echo "[INFO] Shortcut created on desktop."
  fi
fi

echo -e "\n[OK] Done."
sleep 1
