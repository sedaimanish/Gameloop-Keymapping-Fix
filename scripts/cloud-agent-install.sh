#!/usr/bin/env bash
#
# Idempotent Cloud Agent bootstrap for the GameLoop Keymapping Fix repo.
#
# This project is a set of PowerShell installer scripts, so the dev toolchain is
# PowerShell Core (pwsh) plus PSScriptAnalyzer (lint) and Pester (tests). Both
# steps are safe to re-run: pwsh is installed only when missing, and modules are
# installed only when not already present.
set -euo pipefail

# --- PowerShell Core -------------------------------------------------------
if ! command -v pwsh >/dev/null 2>&1; then
    echo "Installing PowerShell Core..."
    # shellcheck disable=SC1091
    . /etc/os-release
    tmpdeb="$(mktemp --suffix=.deb)"
    curl -fsSL "https://packages.microsoft.com/config/ubuntu/${VERSION_ID}/packages-microsoft-prod.deb" -o "$tmpdeb"
    sudo dpkg -i "$tmpdeb"
    rm -f "$tmpdeb"
    sudo apt-get update -qq
    sudo apt-get install -y -qq powershell
else
    echo "PowerShell already installed: $(pwsh --version)"
fi

# --- PowerShell modules (lint + test) --------------------------------------
pwsh -NoProfile -Command '
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted
    foreach ($m in "PSScriptAnalyzer", "Pester") {
        if (-not (Get-Module -ListAvailable -Name $m)) {
            Write-Host "Installing $m ..."
            Install-Module -Name $m -Scope CurrentUser -Force -SkipPublisherCheck
        } else {
            Write-Host "$m already installed"
        }
    }
    Get-Module -ListAvailable PSScriptAnalyzer, Pester |
        Select-Object Name, Version | Sort-Object Name -Unique | Format-Table -AutoSize
'

echo "Bootstrap complete."
