#!/usr/bin/env bash
#
# Thorlabs TDC001 GUI one-click launcher
# • builds / pulls the “gui” service from docker-compose.frontend.yml
# • starts (or restarts) the container
# • opens http://localhost:6080
# • optionally plants a desktop shortcut
#

################### configuration ########################################
compose_relative="../Code/TDC001-project/docker-compose.frontend.yml"
service="tdc_frontend" # docker-compose service name
port=6080              # noVNC external port
shortcut_name="TDC001 GUI.desktop"
icon_path="$(dirname "$0")/tdc_gui.png" # optional .png next to this script
##########################################################################

echo -e "\n\e[36m──────── Thorlabs TDC001 GUI launcher ────────\e[0m\n"

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

# 4) wait for noVNC ------------------------------------------------------
printf "[INFO] Waiting for noVNC on localhost:%d" "$port"
for _ in {1..30}; do
  if curl -s "http://localhost:$port" &>/dev/null; then
    echo " – ready!"
    break
  fi
  printf "."
  sleep 0.5
done

# 5) open browser --------------------------------------------------------
echo "[INFO] Opening browser…"
xdg-open "http://localhost:$port" &>/dev/null &

# 6) desktop shortcut (ask once) ----------------------------------------
desk="$HOME/Desktop"
link="$desk/$shortcut_name"
if [[ ! -e "$link" && -d "$desk" ]]; then
  read -p "Create a desktop shortcut for the GUI? [y/N] " ans
  if [[ ${ans,,} == y* ]]; then
    cat >"$link" <<EOF
[Desktop Entry]
Type=Application
Name=Thorlabs TDC001 GUI
Comment=Start the TDC001 Frontend
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
