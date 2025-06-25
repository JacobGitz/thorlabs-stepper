#!/usr/bin/env bash
#
# Thorlabs TDC001 GUI one-click launcher
# • optionally rebuilds the image
# • starts (or restarts) the container
# • opens http://localhost:6080
#

################### configuration ########################################
compose_relative="../Code/TDC001-project/docker-compose.frontend.yml"
service="tdc_frontend" # docker-compose service name
port=6080              # noVNC external port
##########################################################################

echo -e "\n\e[36m──────── Thorlabs TDC001 GUI launcher ────────\e[0m\n"

# 1) locate compose file -------------------------------------------------
script_dir="$(cd -- "$(dirname "$0")" && pwd)"
compose_file="$(realpath "$script_dir/$compose_relative")"

[[ -f $compose_file ]] || {
  echo -e "\e[31m[ERROR]\e[0m Compose file not found: $compose_file"
  exit 1
}
echo "[INFO] Compose file  $compose_file"

# 2) docker available? ---------------------------------------------------
command -v docker &>/dev/null || {
  echo -e "\e[31m[ERROR]\e[0m Docker CLI not found"
  exit 1
}
docker info &>/dev/null || {
  echo -e "\e[31m[ERROR]\e[0m Docker daemon not running"
  exit 1
}

# 3) does an image already exist? ---------------------------------------
image_id=$(docker compose -f "$compose_file" images -q "$service" 2>/dev/null | head -n 1)

rebuild=false
if [[ -n $image_id ]]; then
  echo "[INFO] Found existing image for $service ($image_id)"
  read -p "Rebuild it? [y/N] " ans
  [[ ${ans,,} == y* ]] && rebuild=true
else
  rebuild=true # no image yet → must build
fi

# 4) build (if requested) -----------------------------------------------
if $rebuild; then
  echo "[INFO] Building image…"
  docker compose -f "$compose_file" build --pull "$service" || {
    echo -e "\e[31m[ERROR]\e[0m Build failed"
    exit 1
  }
fi

# 5) up / recreate container --------------------------------------------
echo "[INFO] (re)creating container…"
docker compose -f "$compose_file" up -d --force-recreate "$service" || {
  echo -e "\e[31m[ERROR]\e[0m docke<#  Thorlabs TDC001 GUI one-click launcher  (PowerShell)
    • asks to rebuild only when an image already exists
    • starts (or recreates) the container
    • opens http://localhost:6080
#>

$ErrorActionPreference = 'Stop'

# ───────── configuration ─────────
$composeRelative = "..\Code\TDC001-project\docker-compose.frontend.yml"
$service         = "tdc_frontend"
$port            = 6080
# ─────────────────────────────────

Write-Host "`n──────── Thorlabs TDC001 GUI launcher ────────`n" -Foreground Cyan

# 1) locate compose file -------------------------------------------------
$scriptDir  = Split-Path $MyInvocation.MyCommand.Path -Parent
try   { $composeFile = Resolve-Path (Join-Path $scriptDir $composeRelative) }
catch { Write-Host "[ERROR] Compose file not found." -Foreground Red; return }

Write-Host "[INFO] Compose file  $composeFile"

# 2) docker available? ---------------------------------------------------
try { docker info | Out-Null }
catch { Write-Host "[ERROR] Docker Desktop is not running." -Foreground Red; return }

# 3) image check / rebuild prompt ---------------------------------------
$imageId = docker compose -f $composeFile images -q $service 2>$null | Select-Object -First 1
$rebuild = $true
if ($imageId) {
    Write-Host "[INFO] Found existing image for $service ($imageId)"
    $rebuild = (Read-Host "Rebuild it? [y/N]") -match '^[Yy]'
}

if ($rebuild) {
    Write-Host "[INFO] Building image…"
    docker compose -f $composeFile build --pull $service
    if ($LASTEXITCODE) { Write-Host "[ERROR] Build failed." -Foreground Red; return }
}

# 4) start / recreate container -----------------------------------------
Write-Host "[INFO] (re)creating container…"
docker compose -f $composeFile up -d --force-recreate $service
if ($LASTEXITCODE) { Write-Host "[ERROR] docker compose failed." -Foreground Red; return }

# 5) wait for noVNC ------------------------------------------------------
Write-Host "[INFO] Waiting for noVNC on localhost:$port"
for ($i=0; $i -lt 30; $i++) {
    try {
        Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$port" -TimeoutSec 1 | Out-Null
        break
    } catch { Start-Sleep -Milliseconds 500 }
}

# 6) open browser --------------------------------------------------------
Write-Host "[INFO] Opening browser…"
Start-Process "http://localhost:$port"

Write-Host "`n[OK] Done."r compose failed"
  exit 1
}

# 6) wait for noVNC ------------------------------------------------------
printf "[INFO] Waiting for noVNC on localhost:%d" "$port"
for _ in {1..30}; do
  if curl -s "http://localhost:$port" &>/dev/null; then
    echo " – ready!"
    break
  fi
  printf "."
  sleep 0.5
done

# 7) open browser --------------------------------------------------------
echo "[INFO] Opening browser…"
xdg-open "http://localhost:$port" &>/dev/null &

echo -e "\n[OK] Done."
sleep 1
