param(
    [string]$ProjectRoot,
    [string]$WorkspaceId
)

$ErrorActionPreference = "Stop"

$BackendRoot = Join-Path $ProjectRoot "backend\server"
$DataRoot = Join-Path $BackendRoot "data"
$WorkspaceRoot = Join-Path $DataRoot "udare_store\$WorkspaceId"
$ArticlesRoot = Join-Path $WorkspaceRoot "articles"
$IndexPath = Join-Path $WorkspaceRoot "index.html"
$InspectionRoot = Join-Path $DataRoot "runtime\inspection"

Write-Host ""
Write-Host "============================================================"
Write-Host "PHASE 4.4.1 — FOCUSED STRUCTURAL DIAGNOSIS"
Write-Host "============================================================"

# ------------------------------------------------------------
# 1. ARTICLE COUNT
# ------------------------------------------------------------

$ArticleFiles = @(
    Get-ChildItem `
        -Path $ArticlesRoot `
        -Filter "*.html" `
        -File `
        -Recurse `
        -ErrorAction Stop
)

$ExpectedCount = 2225
$ActualCount = $ArticleFiles.Count
$CountDifference = $ExpectedCount - $ActualCount

Write-Host ""
Write-Host "1. UDARE ARTICLE COUNT"
Write-Host "Expected:              $ExpectedCount"
Write-Host "Found:                 $ActualCount"
Write-Host "Difference:            $CountDifference"

if ($ActualCount -eq $ExpectedCount) {
    Write-Host "Count integrity:       PASS"
}
else {
    Write-Host "Count integrity:       FAIL"
}

# ------------------------------------------------------------
# 2. INDEX.HTML VERIFICATION
# ------------------------------------------------------------

Write-Host ""
Write-Host "2. UDARE INDEX VERIFICATION"

if (Test-Path $IndexPath) {
    $IndexHtml = Get-Content `
        -Path $IndexPath `
        -Raw `
        -Encoding utf8

    $IndexLinks = @(
        [regex]::Matches(
            $IndexHtml,
            'href\s*=\s*["'']([^"'']*articles/[^"'']+\.html)["'']',
            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
        ) |
        ForEach-Object {
            $_.Groups[1].Value
        } |
        Sort-Object -Unique
    )

    $MissingIndexTargets = @()

    foreach ($Link in $IndexLinks) {
        $DecodedLink = [System.Uri]::UnescapeDataString($Link)
        $RelativePath = $DecodedLink -replace '/', '\'
        $TargetPath = Join-Path $WorkspaceRoot $RelativePath

        if (-not (Test-Path $TargetPath)) {
            $MissingIndexTargets += $Link
        }
    }

    Write-Host "Index exists:          PASS"
    Write-Host "Unique article links:  $($IndexLinks.Count)"
    Write-Host "Missing link targets:  $($MissingIndexTargets.Count)"

    if ($MissingIndexTargets.Count -gt 0) {
        Write-Host ""
        Write-Host "INDEX LINKS WITH MISSING HTML FILES"

        $MissingIndexTargets |
            Select-Object -First 30 |
            ForEach-Object {
                Write-Host "  $_"
            }
    }
}
else {
    Write-Host "Index exists:          FAIL"
}

# ------------------------------------------------------------
# 3. LATEST PRELIMINARY CSV
# ------------------------------------------------------------

Write-Host ""
Write-Host "3. PRELIMINARY STRUCTURAL FAILURE BREAKDOWN"

$LatestCsv = Get-ChildItem `
    -Path $InspectionRoot `
    -Filter "website_article_structure_results_*.csv" `
    -File `
    -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $LatestCsv) {
    Write-Host "Latest structure CSV:  NOT FOUND"
}
else {
    Write-Host "CSV: $($LatestCsv.FullName)"

    $Rows = @(Import-Csv -Path $LatestCsv.FullName)

    $FailedRows = @(
        $Rows |
        Where-Object {
            $_.BasicStructurePass -eq "False"
        }
    )

    Write-Host "Rows scanned:          $($Rows.Count)"
    Write-Host "Failed rows:           $($FailedRows.Count)"

    $Checks = @(
        "HasHtml",
        "HasHead",
        "HasBody",
        "HasTitle",
        "HasH1",
        "HasContentContainer",
        "HasClosingBody",
        "HasClosingHtml"
    )

    Write-Host ""
    Write-Host "FAILURE COUNTS BY CONDITION"

    foreach ($Check in $Checks) {
        $FailureCount = @(
            $FailedRows |
            Where-Object {
                $_.$Check -eq "False"
            }
        ).Count

        Write-Host ("  {0,-24} {1}" -f $Check, $FailureCount)
    }

    $EmptyBodyCount = @(
        $FailedRows |
        Where-Object {
            [int64]$_.VisibleTextLength -le 0
        }
    ).Count

    Write-Host ("  {0,-24} {1}" -f "EmptyVisibleText", $EmptyBodyCount)

    Write-Host ""
    Write-Host "FIRST 30 PRELIMINARY FAILURES"

    foreach ($Row in ($FailedRows | Select-Object -First 30)) {
        $Reasons = @()

        foreach ($Check in $Checks) {
            if ($Row.$Check -eq "False") {
                $Reasons += $Check
            }
        }

        if ([int64]$Row.VisibleTextLength -le 0) {
            $Reasons += "EmptyVisibleText"
        }

        Write-Host ""
        Write-Host "  File:    $($Row.FileName)"
        Write-Host "  Text:    $($Row.VisibleTextLength)"
        Write-Host "  Reasons: $($Reasons -join ', ')"
    }
}

# ------------------------------------------------------------
# 4. EXISTING INTEGRITY IMPLEMENTATION
# ------------------------------------------------------------

Write-Host ""
Write-Host "4. EXISTING INTEGRITY-RELATED PYTHON FILES"

$PythonFiles = @(
    Get-ChildItem `
        -Path $BackendRoot `
        -Filter "*.py" `
        -File `
        -Recurse |
    Where-Object {
        $_.FullName -notmatch `
            '\\(__pycache__|\.venv|venv|node_modules|data)\\'
    }
)

$IntegrityFiles = @(
    $PythonFiles |
    Where-Object {
        $_.Name -match `
            'integrity|website_article|article_structure|corruption|truncation|quarantine'
    }
)

Write-Host "Files found:           $($IntegrityFiles.Count)"

foreach ($File in $IntegrityFiles) {
    Write-Host "  $($File.FullName)"
}

# ------------------------------------------------------------
# 5. EXISTING DEFINITIONS AND RUNTIME WIRING
# ------------------------------------------------------------

Write-Host ""
Write-Host "5. EXISTING DEFINITIONS AND RUNTIME WIRING"

$Patterns = @(
    'class\s+.*Integrity',
    'def\s+.*integrity',
    'def\s+.*structure',
    'def\s+.*corruption',
    'def\s+.*truncation',
    'website_article_integrity',
    'integrity_report',
    'integrity_certification',
    'quarantine',
    'job_type.*integrity',
    'integrity.*worker',
    'integrity.*queue'
)

foreach ($Pattern in $Patterns) {
    $Matches = @(
        Select-String `
            -Path $PythonFiles.FullName `
            -Pattern $Pattern `
            -CaseSensitive:$false `
            -ErrorAction SilentlyContinue
    )

    if ($Matches.Count -gt 0) {
        Write-Host ""
        Write-Host "PATTERN: $Pattern"

        foreach ($Match in ($Matches | Select-Object -First 40)) {
            Write-Host (
                "  {0}:{1}: {2}" -f `
                    $Match.Path,
                    $Match.LineNumber,
                    $Match.Line.Trim()
            )
        }
    }
}

# ------------------------------------------------------------
# 6. UDARE MANIFEST AND BUILD EVIDENCE
# ------------------------------------------------------------

Write-Host ""
Write-Host "6. UDARE MANIFEST AND BUILD-EVIDENCE FILES"

$EvidenceFiles = @(
    Get-ChildItem `
        -Path $WorkspaceRoot `
        -File `
        -Recurse `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @(
            ".json",
            ".jsonl",
            ".csv",
            ".txt"
        )
    }
)

Write-Host "Evidence files found:  $($EvidenceFiles.Count)"

foreach ($File in $EvidenceFiles) {
    Write-Host (
        "  {0} | {1} bytes" -f `
            $File.FullName,
            $File.Length
    )
}

Write-Host ""
Write-Host "COUNT/FAILURE REFERENCES IN EVIDENCE FILES"

$EvidenceMatches = @(
    Select-String `
        -Path $EvidenceFiles.FullName `
        -Pattern `
            '2225|2222|failed|failure|missing|error|quarantine' `
        -CaseSensitive:$false `
        -ErrorAction SilentlyContinue |
    Select-Object -First 100
)

if ($EvidenceMatches.Count -eq 0) {
    Write-Host "  No relevant references found."
}
else {
    foreach ($Match in $EvidenceMatches) {
        Write-Host (
            "  {0}:{1}: {2}" -f `
                $Match.Path,
                $Match.LineNumber,
                $Match.Line.Trim()
        )
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "FOCUSED DIAGNOSIS COMPLETE — READ ONLY"
Write-Host "============================================================"
