param(
    [string]$AppJs = ".\frontend\public\assets\js\app.js",
    [string]$Html  = ".\frontend\public\index.html"
)

$ErrorActionPreference = "Stop"

function Show-Result {
    param(
        [string]$Code,
        [string]$Status,
        [string]$Message
    )
    Write-Host ($Code + " — " + $Status + " — " + $Message)
}

Write-Host ""
Write-Host "===== PHASE 1 — FRONTEND ENTRY TRIGGER CHECK ====="
Write-Host ""

if (-not (Test-Path $AppJs)) {
    Write-Host ("FAIL: app.js not found: " + $AppJs)
    exit 1
}

$js = Get-Content $AppJs -Raw

if (Test-Path $Html) {
    $htmlText = Get-Content $Html -Raw
} else {
    $htmlText = ""
}

# ------------------------------------------------
# 1.1 Bulk Auto-Link button existence
# ------------------------------------------------

if ($htmlText.Contains("btnAutoLinkMain") -or $htmlText.Contains("Bulk Auto-Link")) {
    Show-Result -Code "1.1.1" -Status "PASS" -Message "Bulk Auto-Link button text/id found in HTML"
}
else {
    Show-Result -Code "1.1.1" -Status "WARN" -Message "Could not verify button in HTML (may be rendered dynamically)"
}

$idNeedle1 = 'id="btnAutoLinkMain"'
$idNeedle2 = "id='btnAutoLinkMain'"

if ($htmlText.Contains($idNeedle1) -or $htmlText.Contains($idNeedle2)) {
    Show-Result -Code "1.1.2" -Status "PASS" -Message "Correct DOM id found: btnAutoLinkMain"
}
else {
    Show-Result -Code "1.1.2" -Status "WARN" -Message "Exact DOM id not found in HTML"
}

$idCount = 0
$idCount += ([regex]::Matches($htmlText, 'id="btnAutoLinkMain"')).Count
$idCount += ([regex]::Matches($htmlText, "id='btnAutoLinkMain'")).Count

if ($idCount -le 1) {
    Show-Result -Code "1.1.3" -Status "PASS" -Message ("No duplicate btnAutoLinkMain id detected; count=" + $idCount)
}
else {
    Show-Result -Code "1.1.3" -Status "FAIL" -Message ("Duplicate btnAutoLinkMain ids found: " + $idCount)
}

# ------------------------------------------------
# 1.2 Button event binding
# ------------------------------------------------

if ($js.Contains("btnAutoLinkMain")) {
    Show-Result -Code "1.2.1" -Status "PASS" -Message "btnAutoLinkMain found in app.js"
}
else {
    Show-Result -Code "1.2.1" -Status "FAIL" -Message "btnAutoLinkMain not found in app.js"
}

$hasClickListener = $false
if ($js.Contains("btnAutoLinkMain.addEventListener(""click""")) { $hasClickListener = $true }
if ($js.Contains("btnAutoLinkMain.addEventListener('click'")) { $hasClickListener = $true }
if ($js.Contains("btnAutoLinkMain.onclick =")) { $hasClickListener = $true }

if ($hasClickListener) {
    Show-Result -Code "1.2.2" -Status "PASS" -Message "Click listener attached"
}
else {
    Show-Result -Code "1.2.2" -Status "FAIL" -Message "No click listener found"
}

$hasBulkFlow = $false
if ($js.Contains("runPipelineAndHighlight(")) { $hasBulkFlow = $true }
if ($js.Contains("apiEngineRun(")) { $hasBulkFlow = $true }

if ($hasBulkFlow) {
    Show-Result -Code "1.2.3" -Status "PASS" -Message "Bulk flow function found"
}
else {
    Show-Result -Code "1.2.3" -Status "WARN" -Message "Could not verify intended bulk pipeline flow"
}

$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($null -ne $nodeCmd) {
    $tmp = Join-Path $env:TEMP "phase1_check_temp.js"
    Set-Content -Path $tmp -Value $js -Encoding UTF8
    node --check $tmp *> $null
    if ($LASTEXITCODE -eq 0) {
        Show-Result -Code "1.2.4" -Status "PASS" -Message "No syntax error detected by node --check"
    }
    else {
        Show-Result -Code "1.2.4" -Status "FAIL" -Message "Syntax error detected in app.js"
    }
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
else {
    Show-Result -Code "1.2.4" -Status "WARN" -Message "Node not installed, syntax check skipped"
}

# ------------------------------------------------
# 1.3 Click action execution (runtime-sensitive)
# ------------------------------------------------

Show-Result -Code "1.3.1" -Status "WARN" -Message "Requires browser runtime click test"
Show-Result -Code "1.3.2" -Status "WARN" -Message "Requires runtime validation path test"
Show-Result -Code "1.3.3" -Status "WARN" -Message "Requires runtime execution trace"
Show-Result -Code "1.3.4" -Status "WARN" -Message "Requires runtime guard-clause inspection"

Write-Host ""
Write-Host "===== END PHASE 1 CHECK ====="