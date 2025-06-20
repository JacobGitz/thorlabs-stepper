<#
  Thorlabs TDC001 GUI one-click launcher (NO auto-start)
  • builds / pulls the “gui” service from Code/TDC001-Project/Docker-Compose.frontend.yml
  • starts (or restarts) the container
  • opens http://localhost:6080
  • optionally plants a desktop shortcut
#>

# ───────────────────────── configuration ─────────────────────────
$composeRelative = "..\Code\TDC001-Project\Docker-Compose.frontend.yml"
$service         = "gui"           # docker-compose service name
$port            = 6080            # noVNC external port
$shortcutName    = "TDC001 GUI.lnk"
$iconPath        = "$PSScriptRoot\tdc_gui.ico"  # optional .ico next to this script
# -----------------------------------------------------------------

Write-Host "`n──────── Thorlabs TDC001 GUI launcher ────────`n" -ForegroundColor Cyan

# 1) locate compose file ------------------------------------------------------
$composeFile = Resolve-Path -Path (Join-Path $PSScriptRoot $composeRelative) -ErrorAction Stop
Write-Host "[INFO] Compose file  $composeFile"

# 2) docker available? --------------------------------------------------------
try { docker info | Out-Null }
catch {
    Write-Host "[ERROR] Docker Desktop is not running." -ForegroundColor Red
    Pause
    Exit 1
}

# 3) pull / build & start service --------------------------------------------
Write-Host "[INFO] (re)creating container…"
docker compose -f $composeFile up -d $service
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] docker compose failed." -ForegroundColor Red
    Pause; Exit 1
}

# 4) wait for noVNC -----------------------------------------------------------
Write-Host "[INFO] Waiting for noVNC on localhost:$port"
for ($i=0; $i -lt 30; $i++) {
    try {
        Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$port" -TimeoutSec 1 | Out-Null
        break
    } catch { Start-Sleep -Milliseconds 500 }
}
Write-Host "[INFO] Opening browser…"
Start-Process "http://localhost:$port"

# 5) desktop shortcut (ask once) ---------------------------------------------
$desk = [Environment]::GetFolderPath("Desktop")
$link = Join-Path $desk $shortcutName
if (-not (Test-Path $link)) {
    $ans = [System.Windows.MessageBox]::Show(
        "Create a desktop shortcut for the TDC001 GUI?",
        "TDC001 GUI",
        "YesNo","Question"
    )
    if ($ans -eq "Yes") {
        $WshShell = New-Object -ComObject WScript.Shell
        $shortcut = $WshShell.CreateShortcut($link)
        $shortcut.TargetPath      = $MyInvocation.MyCommand.Definition
        $shortcut.WorkingDirectory = $PSScriptRoot
        if (Test-Path $iconPath) { $shortcut.IconLocation = $iconPath }
        $shortcut.Save()
        Write-Host "[INFO] Shortcut created on desktop."
    }
}

Write-Host "`n[OK] Done."
Start-Sleep 1

