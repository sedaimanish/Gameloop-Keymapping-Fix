# ============================================================
#  GameLoop Keymapping Fix — Client Installer
#  Made by MANISH SEDAI  |  sedaimanish.vercel.app
#
#  No Python required. Downloads pre-patched files from GitHub,
#  applies GameLoop registry tweaks, updates hosts, deletes TVM.
#
#  Run via GameloopFix-Loader.bat (downloads this script from Releases).
# ============================================================

[CmdletBinding()]
param(
    [string]$InstallRoot = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 1.0

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force -ErrorAction SilentlyContinue
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }
$ProgressPreference = 'SilentlyContinue'

# --- GitHub release (edit if you fork) ---
$GithubOwner      = 'sedaimanish'
$GithubRepo       = 'Gameloop-Keymapping-Fix'
$GithubReleaseTag = ''
$PayloadAssetName = 'payload.zip'

$PayloadFiles = @(
    'DefaultKeyMapping.xml'
    'smk.conf'
    'smka.conf'
    'GameSidebar.xml'
    'translate.conf'
    'AEngine.dll'
)

# ==================== UTF-8 CONSOLE ====================
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding           = [System.Text.Encoding]::UTF8
    chcp 65001 | Out-Null
} catch { }

# ==================== ADMIN ====================
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host ''
    Write-Host '   ERROR: Run as Administrator (required for hosts + Program Files).' -Fore Red
    Write-Host '   Right-click GameloopFix-Loader.bat -> Run as administrator' -Fore Yellow
    Read-Host '   Press Enter to exit'
    exit 1
}

# ==================== GLYPHS ====================
function U { param([int[]]$cp) return (-join ($cp | ForEach-Object { [char]$_ })) }
$G = @{
    OK = U 0x221A; XX = U 0x00D7; AR = U 0x2192
}

# ==================== PATHS ====================
function Normalize-InstallRoot {
    param([string]$Root)
    if ([string]::IsNullOrWhiteSpace($Root)) { return $null }
    $r = $Root.Trim().Trim('"').TrimEnd('\')
    if (-not $r) { return $null }
    if (Test-Path -LiteralPath $r) { return $r }
    return $null
}

if (-not $InstallRoot -and $env:GAMEFIX_INSTALLROOT) {
    $InstallRoot = $env:GAMEFIX_INSTALLROOT
}
$resolvedRoot = Normalize-InstallRoot $InstallRoot
if ($resolvedRoot) {
    $ClientDir = $resolvedRoot
} else {
    $ClientDir = Join-Path $env:USERPROFILE 'GameloopFix'
    if (-not (Test-Path -LiteralPath $ClientDir)) {
        New-Item -ItemType Directory -Path $ClientDir -Force | Out-Null
    }
}
$BackupDir = Join-Path $ClientDir 'Backup'
$Manifest  = Join-Path $BackupDir 'backup_manifest.txt'
$WorkDir   = Join-Path $env:TEMP ("GLKeymapFix_" + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$RegPath   = 'HKCU:\Software\Tencent\MobileGamePC'
$tvmPath   = Join-Path $env:APPDATA 'AndroidTbox\TVM_100.xml'
$hostsPath = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
$HOSTS_BEGIN = '# BEGIN GAMELOOP-KEYMAP-FIX'
$HOSTS_END   = '# END GAMELOOP-KEYMAP-FIX'
$DefaultHosts = @(
    '127.0.0.1 conf.syzs.qq.com'
    '127.0.0.1 pm.myapp.com'
    '127.0.0.1 unifiedaccess.gameloop.com'
)

$UIFolder = $null
foreach ($base in @('Program Files', 'Program Files (x86)')) {
    foreach ($d in @('C', 'D', 'E', 'F', 'G')) {
        $cand = "${d}:\$base\TxGameAssistant\ui"
        if (Test-Path $cand) { $UIFolder = $cand; break }
    }
    if ($UIFolder) { break }
}

$AdaptedApks = @(
    'com.tencent.ig', 'com.pubg.krmobile', 'com.pubg.krmobile_ss',
    'com.pubg.twmobile', 'com.vng.pubgmobile', 'com.pubg.imobile'
)
$PkgMap = [ordered]@{
    'Global'  = @('com.tencent.ig')
    'Korean'  = @('com.pubg.krmobile')
    'Taiwan'  = @('com.pubg.twmobile')
    'Vietnam' = @('com.vng.pubgmobile')
    'BGMI'    = @('com.pubg.imobile')
}
$AlwaysTwin = @('com.pubg.krmobile')
$AllVersionKeys = @('Global', 'Korean', 'Taiwan', 'Vietnam', 'BGMI')

# ==================== PROCESS CONTROL ====================
function Stop-GameLoop {
    $procs = @('AndroidEmulatorEn', 'AndroidEmulatorEx', 'AndroidEmulator', 'AppMarket',
               'GameLoop', 'TxGameAssistant', 'aow_exe', 'AowStore', 'GameLoopVMM',
               'TxGameDownload', 'AndroidRenderer', 'GameLoopHelper', 'QMEmulatorService',
               'TenioDL', 'txnotifycenter')
    $killed = 0
    foreach ($p in $procs) {
        $running = Get-Process -Name $p -ErrorAction SilentlyContinue
        if ($running) { $running | Stop-Process -Force -ErrorAction SilentlyContinue; $killed++ }
    }
    if ($killed -gt 0) { Start-Sleep -Milliseconds 1800 }
    return $killed
}

# ==================== UI HELPERS ====================
function Write-Title { param([string]$Text)
    Write-Host ''; Write-Host ("  == $Text ==") -Fore Cyan; Write-Host ''
}
function Read-Choice {
    param([string]$Prompt, [hashtable]$Options, [string]$Default)
    Write-Host "   $Prompt" -Fore Yellow
    foreach ($k in ($Options.Keys | Sort-Object)) {
        $mark = if ($k -eq $Default) { ' (default)' } else { '' }
        Write-Host ("      [{0}] {1}{2}" -f $k, $Options[$k], $mark)
    }
    $a = Read-Host '   Select'
    if ([string]::IsNullOrWhiteSpace($a) -or -not $Options.ContainsKey($a)) { return $Default }
    return $a
}
function Read-YesNo {
    param([string]$Prompt, [string]$Default = 'N')
    Write-Host "   $Prompt  [Y/N]  (default $Default)"
    $a = (Read-Host '   Select').Trim().ToUpper()
    if ($a -ne 'Y' -and $a -ne 'N') { $a = $Default }
    return ($a -eq 'Y')
}
function Read-Number {
    param([string]$Prompt, [int]$Min, [int]$Max, [int]$Default)
    Write-Host "   $Prompt  [$Min-$Max]  (default $Default)"
    $a = Read-Host '   Enter'
    $n = 0
    if ([int]::TryParse($a, [ref]$n) -and $n -ge $Min -and $n -le $Max) { return $n }
    return $Default
}

# ==================== REGISTRY ====================
function Set-Reg {
    param([string]$Name, [string]$Hex)
    $val = [Convert]::ToInt32($Hex, 16)
    if (-not (Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }
    Set-ItemProperty -Path $RegPath -Name $Name -Value $val -Type DWord -Force
}
function Get-RegHex {
    param([string]$Name)
    try {
        $cur = Get-ItemProperty -Path $RegPath -ErrorAction Stop
        if ($null -ne $cur.PSObject.Properties[$Name]) { return ('{0:x}' -f [int]$cur.$Name) }
    } catch { }
    return $null
}
function Test-RegPackageExists {
    param([string]$Pkg)
    try {
        $cur = Get-ItemProperty -Path $RegPath -ErrorAction Stop
        foreach ($suffix in @('_ContentScale', '_FPSLevel', '_RenderQuality')) {
            if ($null -ne $cur.PSObject.Properties["$Pkg$suffix"]) { return $true }
        }
    } catch { }
    return $false
}
function Get-Packages {
    param([string[]]$Versions)
    $out = @()
    foreach ($v in $Versions) {
        foreach ($p in $PkgMap[$v]) {
            if ($out -notcontains $p) { $out += $p }
            $twin = $p + '_ss'
            if (($AlwaysTwin -contains $p) -or (Test-RegPackageExists $twin)) {
                if ($out -notcontains $twin) { $out += $twin }
            }
        }
    }
    return $out
}
function Set-AdaptedApkList {
    param([string[]]$Packages)
    $existing = $null
    try {
        $cur = Get-ItemProperty -Path $RegPath -ErrorAction Stop
        if ($null -ne $cur.PSObject.Properties['AdaptedApkList']) { $existing = [string]$cur.AdaptedApkList }
    } catch { }
    $sep = ';'
    if ($existing -and $existing.Contains(',') -and -not $existing.Contains(';')) { $sep = ',' }
    $list = @()
    if ($existing) {
        foreach ($e in ($existing -split '[;,]')) {
            $e = $e.Trim()
            if ($e -and ($list -notcontains $e)) { $list += $e }
        }
    }
    foreach ($pk in $Packages) {
        if ($list -notcontains $pk) { $list += $pk }
    }
    $value = ($list -join $sep)
    if (-not (Test-Path $RegPath)) { New-Item -Path $RegPath -Force | Out-Null }
    Set-ItemProperty -Path $RegPath -Name 'AdaptedApkList' -Value $value -Type String -Force
}

# ==================== BACKUP ====================
function Backup-Once {
    param([string]$Path, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return 'missing' }
    if ((Get-Item -LiteralPath $Path).Length -lt 1) { return 'empty' }
    if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null }
    $dst = Join-Path $BackupDir $Key
    if (Test-Path -LiteralPath $dst) { return 'exists' }
    Copy-Item -LiteralPath $Path $dst -Force
    Add-Content -LiteralPath $Manifest -Encoding ASCII -Value ("{0}`t{1}`t{2}" -f $Key, $Path, (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    return 'archived'
}
function Get-ManifestEntries {
    if (-not (Test-Path -LiteralPath $Manifest)) { return @() }
    $out = @()
    foreach ($line in (Get-Content -LiteralPath $Manifest)) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $p = $line -split "`t"
        if ($p.Count -ge 2) { $out += [pscustomobject]@{ Key = $p[0]; Path = $p[1] } }
    }
    return $out
}

# ==================== HOSTS ====================
function Update-HostsFile {
    $hostsFile = Join-Path $ClientDir 'hosts_entries.txt'
    $entries = @(); $srcLabel = 'built-in list'
    if (Test-Path -LiteralPath $hostsFile) {
        foreach ($raw in (Get-Content -LiteralPath $hostsFile)) {
            $line = $raw.Trim()
            if ($line -eq '' -or $line.StartsWith('#')) { continue }
            if ($line -match '^\S+\s+\S+') { $entries += $line } else { $entries += "127.0.0.1 $line" }
        }
        if ($entries.Count -gt 0) { $srcLabel = 'hosts_entries.txt' }
    }
    if ($entries.Count -eq 0) { $entries = $DefaultHosts }
    if (Test-Path -LiteralPath $hostsPath) {
        (Get-Item -LiteralPath $hostsPath).Attributes = 'Normal'
        $h = [IO.File]::ReadAllText($hostsPath)
    } else { $h = '' }
    $pat = "(?s)\r?\n?" + [regex]::Escape($HOSTS_BEGIN) + ".*?" + [regex]::Escape($HOSTS_END)
    $h = [regex]::Replace($h, $pat, '')
    $block = ($HOSTS_BEGIN, ($entries -join "`r`n"), $HOSTS_END) -join "`r`n"
    [IO.File]::WriteAllText($hostsPath, ($h.TrimEnd() + "`r`n" + $block + "`r`n"), (New-Object Text.ASCIIEncoding))
    & ipconfig /flushdns | Out-Null
    Write-Host "   [$($G.OK)] hosts updated ($srcLabel, $($entries.Count) entries)" -Fore Green
}

# ==================== DOWNLOAD ====================
function Get-ReleaseDownloadUrl {
    param([string]$AssetName)
    $headers = @{ 'User-Agent' = 'GameloopFix-Installer' }
    if ($GithubReleaseTag) {
        $uri = "https://api.github.com/repos/$GithubOwner/$GithubRepo/releases/tags/$GithubReleaseTag"
    } else {
        $uri = "https://api.github.com/repos/$GithubOwner/$GithubRepo/releases/latest"
    }
    $release = Invoke-RestMethod -Uri $uri -Headers $headers -UseBasicParsing
    $asset = @($release.assets | Where-Object { $_.name -eq $AssetName })[0]
    if (-not $asset) {
        throw "Release asset '$AssetName' not found on $($release.tag_name). Upload payload.zip to the release."
    }
    return [string]$asset.browser_download_url
}
function Download-ReleaseFile {
    param(
        [string]$Url,
        [string]$OutFile
    )
    $headers = @{ 'User-Agent' = 'GameloopFix-Installer' }
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        & curl.exe -fsSL --retry 3 --retry-delay 2 -A 'GameloopFix-Installer' -o $OutFile $Url
        if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $OutFile) -and (Get-Item -LiteralPath $OutFile).Length -gt 1000) {
            return
        }
    }
    Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing -Headers $headers
}
function Download-Payload {
    param([string]$DestDir)
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
    $zipPath = Join-Path $env:TEMP ("GLPayload_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.zip')
    Write-Host '   Fetching patched files from GitHub Release...' -Fore Yellow
    $url = Get-ReleaseDownloadUrl -AssetName $PayloadAssetName
    Write-Host "   Source: $url" -Fore Gray
    try {
        Download-ReleaseFile -Url $url -OutFile $zipPath
        $zipKb = [int]((Get-Item -LiteralPath $zipPath).Length / 1024)
        if ($zipKb -lt 10) { throw 'download too small' }
        Write-Host "   Downloaded payload ($zipKb KB)" -Fore Green
        Expand-Archive -LiteralPath $zipPath -DestinationPath $DestDir -Force
    } finally {
        Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
    }
    foreach ($name in $PayloadFiles) {
        $out = Join-Path $DestDir $name
        if (-not (Test-Path -LiteralPath $out)) { throw "Payload zip missing file: $name" }
        $kb = [int]((Get-Item -LiteralPath $out).Length / 1024)
        Write-Host "   [$($G.OK)] $name ($kb KB)" -Fore Green
    }
}

# ==================== KEYMAP PATCH (before install) ====================
function Set-KeymapSmartModeDefault {
    param(
        [string]$KeymapPath,
        [string]$ModeId
    )
    $text = [IO.File]::ReadAllText($KeymapPath)
    $pattern = '(?s)(<(Item|ItemEx)\s+ApkName="([^"]+)"[^>]*>)(.*?)(</\2>)'
    $regex = New-Object System.Text.RegularExpressions.Regex $pattern
    $evaluator = {
        param($m)
        $pkg = $m.Groups[3].Value
        if ($pkg -notmatch '^com\.(?:tencent\.ig|tencent\.tmgp\.pubgm|pubg\.|vng\.|rekoo\.)') { return $m.Value }
        $modeId = $m.ModeId
        $inner = $m.Groups[4].Value
        $inner = [regex]::Replace($inner, '(<LastMode[^>]*?)ModeID="[0-9]+"', ('${1}ModeID="' + $modeId + '"'))
        $inner = [regex]::Replace($inner, '(<Switch Name="SetUp"[^>]*ModeID=")[0-9]+(")', ('${1}' + $modeId + '${2}'))
        $inner = $inner -creplace '(<LastMode[^>]*?)EnableGameKeyDT="0"', '${1}EnableGameKeyDT="1"'
        return $m.Groups[1].Value + $inner + $m.Groups[5].Value
    }
    $wrapped = { param($m) & $evaluator $m }.GetNewClosure()
    # Pass ModeId into evaluator via a simple loop instead (PS 5.1 safe)
    $sb = New-Object System.Text.StringBuilder
    $last = 0
    foreach ($match in $regex.Matches($text)) {
        [void]$sb.Append($text.Substring($last, $match.Index - $last))
        $pkg = $match.Groups[3].Value
        if ($pkg -match '^com\.(?:tencent\.ig|tencent\.tmgp\.pubgm|pubg\.|vng\.|rekoo\.)') {
            $inner = $match.Groups[4].Value
            $inner = [regex]::Replace($inner, '(<LastMode[^>]*?)ModeID="[0-9]+"', ('${1}ModeID="' + $ModeId + '"'))
            $inner = [regex]::Replace($inner, '(<Switch Name="SetUp"[^>]*ModeID=")[0-9]+(")', ('${1}' + $ModeId + '${2}'))
            $inner = $inner -creplace '(<LastMode[^>]*?)EnableGameKeyDT="0"', '${1}EnableGameKeyDT="1"'
            [void]$sb.Append($match.Groups[1].Value + $inner + $match.Groups[5].Value)
        } else {
            [void]$sb.Append($match.Value)
        }
        $last = $match.Index + $match.Length
    }
    [void]$sb.Append($text.Substring($last))
    [IO.File]::WriteAllText($KeymapPath, $sb.ToString())
}

# ==================== CONFIG WIZARD ====================
function Get-AllPackages {
    return Get-Packages -Versions $AllVersionKeys
}
function Select-SmartMode {
    $rc = Read-Choice -Prompt 'Smart keymap mode (game definition)' -Default '2' -Options @{
        '1' = 'Smart 720P'
        '2' = 'Smart 1080P'
        '3' = 'Smart 2K'
    }
    switch ($rc) {
        '1' { return [pscustomobject]@{ Name = 'Smart 720P'; ModeID = '2' } }
        '2' { return [pscustomobject]@{ Name = 'Smart 1080P'; ModeID = '3' } }
        '3' { return [pscustomobject]@{ Name = 'Smart 2K'; ModeID = '4' } }
    }
}
function Select-Definition {
    $rc = Read-Choice -Prompt 'Game definition (resolution)' -Default '2' -Options @{
        '1' = '720P  (SD)'
        '2' = '1080P (HD)'
        '3' = '1440P (2K)'
    }
    switch ($rc) {
        '1' { return [pscustomobject]@{ Hex = '0'; Name = '720P'; ModeID = '2' } }
        '2' { return [pscustomobject]@{ Hex = '1'; Name = '1080P'; ModeID = '3' } }
        '3' { return [pscustomobject]@{ Hex = '2'; Name = '1440P'; ModeID = '4' } }
    }
}
function Invoke-TweaksWizard {
    $pkgs = Get-AllPackages
    $def  = Select-Definition
    $eng = Read-Choice -Prompt 'Render engine' -Default '1' -Options @{
        '1' = 'DirectX+'; '2' = 'OpenGL+'
    }
    $engHex = if ($eng -eq '1') { '1' } else { '0' }
    $fps = Read-Choice -Prompt 'Target FPS' -Default '3' -Options @{
        '1' = '40 FPS'; '2' = '60 FPS'; '3' = '90 FPS'; '4' = '120 FPS'
    }
    switch ($fps) {
        '1' { $fpsHex = '28' }; '2' { $fpsHex = '3c' }
        '3' { $fpsHex = '5a' }; '4' { $fpsHex = '78' }
    }
    $gq = Read-Choice -Prompt 'Graphic quality' -Default '2' -Options @{
        '1' = 'Smooth'; '2' = 'Balanced'; '3' = 'HD'
    }
    switch ($gq) { '1' { $gqHex = '0' }; '2' { $gqHex = '1' }; '3' { $gqHex = '2' } }
    $aa = Read-Choice -Prompt 'Anti-aliasing (FXAA)' -Default '1' -Options @{
        '1' = 'Disabled'; '2' = 'Balanced'; '3' = 'Ultra'
    }
    switch ($aa) { '1' { $aaHex = '0' }; '2' { $aaHex = '1' }; '3' { $aaHex = '2' } }
    $cores   = Read-Number -Prompt 'CPU cores' -Min 1 -Max 10 -Default 8
    $coreHex = '{0:x}' -f $cores
    $ram = Read-Choice -Prompt 'RAM allocation' -Default '2' -Options @{
        '1' = '4 GB'; '2' = '8 GB'; '3' = '12 GB'; '4' = '16 GB'
    }
    switch ($ram) {
        '1' { $ramHex = '1000' }; '2' { $ramHex = '2000' }
        '3' { $ramHex = '3000' }; '4' { $ramHex = '4000' }
    }
    $dpi = Read-Choice -Prompt 'Emulator DPI' -Default '2' -Options @{
        '1' = '240'; '2' = '320'; '3' = '400'; '4' = '480'
    }
    switch ($dpi) {
        '1' { $dpiHex = 'f0' }; '2' { $dpiHex = '140' }
        '3' { $dpiHex = '190' }; '4' { $dpiHex = '1e0' }
    }
    $ipad = Read-YesNo -Prompt 'Enable iPad view (3:2 / 4:3)?' -Default 'N'
    if ($ipad) {
        $res = Read-Choice -Prompt 'iPad resolution' -Default '2' -Options @{
            '1' = '960 x 720'; '2' = '1440 x 1080'; '3' = '1600 x 1200'; '4' = '1920 x 1440'
        }
        switch ($res) {
            '1' { $wHex = '3c0'; $hHex = '2d0' }
            '2' { $wHex = '5a0'; $hHex = '438' }
            '3' { $wHex = '640'; $hHex = '4b0' }
            '4' { $wHex = '780'; $hHex = '5a0' }
        }
    } else {
        $res = Read-Choice -Prompt 'Screen resolution (16:9)' -Default '3' -Options @{
            '1' = '1280 x 720'; '2' = '1600 x 900'; '3' = '1920 x 1080'; '4' = '2560 x 1440'
        }
        switch ($res) {
            '1' { $wHex = '500'; $hHex = '2d0' }
            '2' { $wHex = '640'; $hHex = '384' }
            '3' { $wHex = '780'; $hHex = '438' }
            '4' { $wHex = 'a00'; $hHex = '5a0' }
        }
    }
    return [pscustomobject]@{
        Versions = $AllVersionKeys; Packages = $pkgs; Definition = $def
        EngHex = $engHex; FpsHex = $fpsHex; GqHex = $gqHex; AaHex = $aaHex
        CoreHex = $coreHex; RamHex = $ramHex; DpiHex = $dpiHex
        WHex = $wHex; HHex = $hHex
    }
}
function Apply-RegistryConfig {
    param($Cfg)
    foreach ($p in $Cfg.Packages) {
        Set-Reg -Name "${p}_ContentScale"  -Hex $Cfg.Definition.Hex | Out-Null
        Set-Reg -Name "${p}_FPSLevel"      -Hex $Cfg.FpsHex | Out-Null
        Set-Reg -Name "${p}_RenderQuality" -Hex $Cfg.GqHex | Out-Null
    }
    Set-AdaptedApkList -Packages $AdaptedApks | Out-Null
    Set-Reg -Name 'ForceDirectX'     -Hex $Cfg.EngHex | Out-Null
    Set-Reg -Name 'FxaaQuality'      -Hex $Cfg.AaHex | Out-Null
    Set-Reg -Name 'VMCpuCount'       -Hex $Cfg.CoreHex | Out-Null
    Set-Reg -Name 'VMMemorySizeInMB' -Hex $Cfg.RamHex | Out-Null
    Set-Reg -Name 'VMDPI'            -Hex $Cfg.DpiHex | Out-Null
    Set-Reg -Name 'VMResWidth'       -Hex $Cfg.WHex | Out-Null
    Set-Reg -Name 'VMResHeight'      -Hex $Cfg.HHex | Out-Null
    Write-Host "   [$($G.OK)] Registry written for $($Cfg.Packages.Count) package(s)" -Fore Green
}

# ==================== INSTALL PIPELINE ====================
function Install-PatchedFiles {
    param([string]$SourceDir)
    if (-not $UIFolder) { throw 'GameLoop UI folder not found (TxGameAssistant\ui)' }
    $targets = @{
        'DefaultKeyMapping.xml' = Join-Path $UIFolder 'DefaultKeyMapping.xml'
        'smk.conf'              = Join-Path $UIFolder 'smk.conf'
        'smka.conf'             = Join-Path $UIFolder 'smka.conf'
        'GameSidebar.xml'       = Join-Path $UIFolder 'GameSidebar.xml'
        'translate.conf'        = Join-Path $UIFolder 'translate.conf'
        'AEngine.dll'           = Join-Path $UIFolder 'AEngine.dll'
    }
    foreach ($key in $targets.Keys) {
        $src = Join-Path $SourceDir $key
        if (-not (Test-Path -LiteralPath $src)) { throw "Missing payload file: $key" }
        Backup-Once -Path $targets[$key] -Key $key | Out-Null
        Copy-Item -LiteralPath $src $targets[$key] -Force
        Write-Host "   [$($G.OK)] $key" -Fore Green
    }
    Backup-Once -Path $hostsPath -Key 'hosts' | Out-Null
}

function Remove-TvmFile {
    if (Test-Path -LiteralPath $tvmPath) {
        Backup-Once -Path $tvmPath -Key 'TVM_100.xml' | Out-Null
        Remove-Item -LiteralPath $tvmPath -Force
        Write-Host "   [$($G.OK)] Deleted TVM_100.xml" -Fore Green
    } else {
        Write-Host '   TVM_100.xml not present (OK)' -Fore Gray
    }
}

function Invoke-FullInstall {
    Write-Title 'Smart keymap mode'
    $smart = Select-SmartMode
    Write-Title 'Installing patched keymaps'
    Write-Host '   Stopping GameLoop...' -Fore Yellow
    $killed = Stop-GameLoop
    if ($killed) { Write-Host "   Stopped $killed process group(s)" -Fore Gray }
    New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
    Write-Host '   Downloading patched files from GitHub...' -Fore Yellow
    Download-Payload -DestDir $WorkDir
    $keymapPath = Join-Path $WorkDir 'DefaultKeyMapping.xml'
    Write-Host ("   Setting default LastMode -> ModeID $($smart.ModeID) ($($smart.Name))...") -Fore Yellow
    Set-KeymapSmartModeDefault -KeymapPath $keymapPath -ModeId $smart.ModeID
    Write-Host "   [$($G.OK)] DefaultKeyMapping.xml updated for all PUBG versions" -Fore Green
    Install-PatchedFiles -SourceDir $WorkDir
    Remove-TvmFile
    Write-Host '   Updating hosts file...' -Fore Yellow
    Update-HostsFile
    try { Remove-Item -LiteralPath $WorkDir -Recurse -Force -ErrorAction SilentlyContinue } catch { }
    Write-Host ''
    Write-Host '   ALL DONE. Relaunch GameLoop.' -Fore Cyan
    Write-Host ("   Smart mode: $($smart.Name)  |  All PUBG versions") -Fore Gray
    Write-Host '   Backup saved in Backup\' -Fore Gray
}

function Invoke-ConfigOnly {
    Write-Title 'GameLoop tweaks'
    Stop-GameLoop | Out-Null
    $cfg = Invoke-TweaksWizard
    Apply-RegistryConfig -Cfg $cfg
    Write-Host ''; Write-Host '   Registry updated for all PUBG versions. Relaunch GameLoop.' -Fore Cyan
    Write-Host ("   Definition: $($cfg.Definition.Name)") -Fore Gray
}

function Invoke-Restore {
    Write-Title 'Restore backup'
    $entries = Get-ManifestEntries
    if ($entries.Count -eq 0) {
        Write-Host '   Nothing to restore.' -Fore Yellow
        return
    }
    Stop-GameLoop | Out-Null
    $done = 0
    foreach ($e in $entries) {
        $src = Join-Path $BackupDir $e.Key
        if (-not (Test-Path -LiteralPath $src)) { continue }
        try {
            $parent = Split-Path $e.Path -Parent
            if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            if ($e.Key -eq 'hosts' -and (Test-Path -LiteralPath $e.Path)) {
                (Get-Item -LiteralPath $e.Path).Attributes = 'Normal'
            }
            Copy-Item -LiteralPath $src $e.Path -Force
            Write-Host "   [$($G.OK)] $($e.Key)" -Fore Green
            $done++
        } catch {
            Write-Host "   [$($G.XX)] $($e.Key): $($_.Exception.Message)" -Fore Red
        }
    }
    & ipconfig /flushdns | Out-Null
    Write-Host "   Restored $done file(s)." -Fore Cyan
}

# ==================== MAIN ====================
Clear-Host
Write-Host ''
Write-Host '  GameLoop Keymapping Fix - Client Installer' -Fore Cyan
Write-Host '  Made by MANISH SEDAI  |  sedaimanish.vercel.app' -Fore Gray
if ($UIFolder) { Write-Host ("  UI folder: $UIFolder") -Fore Gray } else { Write-Host '  UI folder: NOT FOUND' -Fore Red }

$menu = Read-Choice -Prompt 'MAIN MENU' -Default '1' -Options @{
    '1' = 'Optimize keymapping'
    '2' = 'GameLoop tweaks'
    '3' = 'Restore backup'
    '4' = 'Exit'
}

switch ($menu) {
    '1' { if (-not $UIFolder) { Write-Host '   Cannot install: GameLoop UI folder missing.' -Fore Red } else { Invoke-FullInstall } }
    '2' { Invoke-ConfigOnly }
    '3' { Invoke-Restore }
    '4' { exit 0 }
}

Write-Host ''
Read-Host '   Press Enter to exit'
