param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId
)

$ErrorActionPreference = "Stop"

$DataRoot = Join-Path $ProjectRoot "backend\server\data"
$UdareRoot = Join-Path $DataRoot "udare_store\$WorkspaceId"
$MetadataRoot = Join-Path $UdareRoot "metadata"
$ManifestPath = Join-Path $UdareRoot "manifests\udare_store_manifest.json"
$InspectionRoot = Join-Path $DataRoot "runtime\inspection"

function Get-FirstValue {
    param(
        [object]$Object,
        [string[]]$Names
    )

    if ($null -eq $Object) {
        return $null
    }

    foreach ($Name in $Names) {
        $Property = $Object.PSObject.Properties[$Name]

        if (
            $null -ne $Property -and
            $null -ne $Property.Value -and
            -not [string]::IsNullOrWhiteSpace(
                [string]$Property.Value
            )
        ) {
            return [string]$Property.Value
        }
    }

    return $null
}

Write-Host ""
Write-Host "============================================================"
Write-Host "UDARE MISSING-THREE DIAGNOSIS"
Write-Host "============================================================"
Write-Host "Workspace: $WorkspaceId"

# ------------------------------------------------------------
# 1. READ UDARE MANIFEST
# ------------------------------------------------------------

Write-Host ""
Write-Host "1. UDARE MANIFEST"

if (-not (Test-Path $ManifestPath)) {
    throw "UDARE manifest was not found: $ManifestPath"
}

$Manifest = Get-Content `
    -Path $ManifestPath `
    -Raw `
    -Encoding utf8 |
    ConvertFrom-Json

Write-Host "Record count:            $($Manifest.record_count)"
Write-Host "Article document count:  $($Manifest.article_document_count)"
Write-Host "Metadata record count:   $($Manifest.metadata_record_count)"

# ------------------------------------------------------------
# 2. READ ALL UDARE METADATA IDENTITIES
# ------------------------------------------------------------

Write-Host ""
Write-Host "2. UDARE METADATA IDENTITIES"

$MetadataFiles = @(
    Get-ChildItem `
        -Path $MetadataRoot `
        -Filter "*.json" `
        -File `
        -ErrorAction Stop
)

$UdareRecords = [System.Collections.Generic.List[object]]::new()

foreach ($File in $MetadataFiles) {
    try {
        $Record = Get-Content `
            -Path $File.FullName `
            -Raw `
            -Encoding utf8 |
            ConvertFrom-Json

        $SourceRecordId = Get-FirstValue `
            -Object $Record `
            -Names @(
                "source_record_id",
                "raw_html_id",
                "record_id",
                "source_id",
                "page_id",
                "document_id",
                "id"
            )

        if ([string]::IsNullOrWhiteSpace($SourceRecordId)) {
            if ($File.BaseName -match '^(raw_html_[0-9a-f]+)') {
                $SourceRecordId = $Matches[1]
            }
        }

        $SourceUrl = Get-FirstValue `
            -Object $Record `
            -Names @(
                "source_url",
                "canonical_url",
                "url",
                "page_url"
            )

        $UdareRecords.Add(
            [PSCustomObject]@{
                source_record_id = $SourceRecordId
                source_url       = $SourceUrl
                metadata_path    = $File.FullName
            }
        )
    }
    catch {
        Write-Host "Unreadable metadata: $($File.FullName)"
    }
}

$UdareIds = @(
    $UdareRecords.source_record_id |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    Sort-Object -Unique
)

$UdareUrls = @(
    $UdareRecords.source_url |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    ForEach-Object {
        $_.Trim().TrimEnd("/").ToLowerInvariant()
    } |
    Sort-Object -Unique
)

Write-Host "Metadata files:         $($MetadataFiles.Count)"
Write-Host "Unique source IDs:      $($UdareIds.Count)"
Write-Host "Unique source URLs:     $($UdareUrls.Count)"

# ------------------------------------------------------------
# 3. DISCOVER RAW HTML STORE
# ------------------------------------------------------------

Write-Host ""
Write-Host "3. RAW HTML STORE DISCOVERY"

$RawStoreDirectories = @(
    Get-ChildItem `
        -Path $DataRoot `
        -Directory `
        -Recurse `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -match 'raw.*html.*store' -and
        $_.FullName -match [regex]::Escape($WorkspaceId)
    } |
    Sort-Object FullName -Unique
)

if ($RawStoreDirectories.Count -eq 0) {
    $RawStoreDirectories = @(
        Get-ChildItem `
            -Path $DataRoot `
            -Directory `
            -Recurse `
            -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -match 'raw.*html.*store'
        } |
        Sort-Object FullName -Unique
    )
}

Write-Host "Candidate directories:  $($RawStoreDirectories.Count)"

foreach ($Directory in $RawStoreDirectories) {
    Write-Host "  $($Directory.FullName)"
}

if ($RawStoreDirectories.Count -eq 0) {
    throw "No Raw HTML Store directory was discovered."
}

# ------------------------------------------------------------
# 4. EXTRACT RAW HTML IDENTITIES
# ------------------------------------------------------------

Write-Host ""
Write-Host "4. RAW HTML IDENTITIES"

$RawFiles = @(
    foreach ($Directory in $RawStoreDirectories) {
        Get-ChildItem `
            -Path $Directory.FullName `
            -File `
            -Recurse `
            -ErrorAction SilentlyContinue
    }
) | Sort-Object FullName -Unique

$RawRecords = [System.Collections.Generic.List[object]]::new()

foreach ($File in $RawFiles) {
    $SourceRecordId = $null
    $SourceUrl = $null

    if ($File.BaseName -match '(raw_html_[0-9a-f]+)') {
        $SourceRecordId = $Matches[1]
    }

    if ($File.Extension -eq ".json") {
        try {
            $Record = Get-Content `
                -Path $File.FullName `
                -Raw `
                -Encoding utf8 |
                ConvertFrom-Json

            $JsonId = Get-FirstValue `
                -Object $Record `
                -Names @(
                    "source_record_id",
                    "raw_html_id",
                    "record_id",
                    "source_id",
                    "page_id",
                    "document_id",
                    "id"
                )

            if (-not [string]::IsNullOrWhiteSpace($JsonId)) {
                $SourceRecordId = $JsonId
            }

            $SourceUrl = Get-FirstValue `
                -Object $Record `
                -Names @(
                    "source_url",
                    "canonical_url",
                    "url",
                    "page_url",
                    "requested_url",
                    "final_url"
                )
        }
        catch {
            # Ignore unrelated or malformed JSON files.
        }
    }

    if (
        -not [string]::IsNullOrWhiteSpace($SourceRecordId) -or
        -not [string]::IsNullOrWhiteSpace($SourceUrl)
    ) {
        $RawRecords.Add(
            [PSCustomObject]@{
                source_record_id = $SourceRecordId
                source_url       = $SourceUrl
                raw_path         = $File.FullName
            }
        )
    }
}

$RawIds = @(
    $RawRecords.source_record_id |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    Sort-Object -Unique
)

$RawUrls = @(
    $RawRecords.source_url |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    ForEach-Object {
        $_.Trim().TrimEnd("/").ToLowerInvariant()
    } |
    Sort-Object -Unique
)

Write-Host "Raw files inspected:    $($RawFiles.Count)"
Write-Host "Unique raw IDs:         $($RawIds.Count)"
Write-Host "Unique raw URLs:        $($RawUrls.Count)"

# ------------------------------------------------------------
# 5. FIND RECORDS ABSENT FROM UDARE
# ------------------------------------------------------------

Write-Host ""
Write-Host "5. RAW RECORDS ABSENT FROM UDARE"

$MissingIds = @(
    $RawIds |
    Where-Object {
        $_ -notin $UdareIds
    }
)

$MissingUrls = @(
    $RawUrls |
    Where-Object {
        $_ -notin $UdareUrls
    }
)

Write-Host "Missing by source ID:   $($MissingIds.Count)"

foreach ($Id in $MissingIds) {
    Write-Host ""
    Write-Host "MISSING ID: $Id"

    $RawRecords |
        Where-Object {
            $_.source_record_id -eq $Id
        } |
        Select-Object -First 5 |
        ForEach-Object {
            Write-Host "  URL:  $($_.source_url)"
            Write-Host "  File: $($_.raw_path)"
        }
}

Write-Host ""
Write-Host "Missing by source URL:  $($MissingUrls.Count)"

foreach ($Url in ($MissingUrls | Select-Object -First 20)) {
    Write-Host "  $Url"
}

# ------------------------------------------------------------
# 6. PRELIMINARY STRUCTURE FAILURE BREAKDOWN
# ------------------------------------------------------------

Write-Host ""
Write-Host "6. PRELIMINARY STRUCTURAL FAILURE BREAKDOWN"

$LatestCsv = Get-ChildItem `
    -Path $InspectionRoot `
    -Filter "website_article_structure_results_*.csv" `
    -File `
    -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $LatestCsv) {
    Write-Host "Structure CSV:          NOT FOUND"
}
else {
    $Rows = @(Import-Csv -Path $LatestCsv.FullName)

    $FailedRows = @(
        $Rows |
        Where-Object {
            $_.BasicStructurePass -eq "False"
        }
    )

    Write-Host "CSV:                    $($LatestCsv.FullName)"
    Write-Host "Rows scanned:           $($Rows.Count)"
    Write-Host "Preliminary failures:   $($FailedRows.Count)"

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

    foreach ($Check in $Checks) {
        $Count = @(
            $FailedRows |
            Where-Object {
                $_.$Check -eq "False"
            }
        ).Count

        Write-Host ("  {0,-24} {1}" -f $Check, $Count)
    }

    $EmptyTextCount = @(
        $FailedRows |
        Where-Object {
            [int64]$_.VisibleTextLength -le 0
        }
    ).Count

    Write-Host ("  {0,-24} {1}" -f "EmptyVisibleText", $EmptyTextCount)
}

Write-Host ""
Write-Host "============================================================"
Write-Host "DIAGNOSIS COMPLETE — NO FILES MODIFIED"
Write-Host "============================================================"
