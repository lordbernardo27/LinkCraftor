param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId
)

$ErrorActionPreference = "Stop"

$DataRoot = Join-Path $ProjectRoot "backend\server\data"

$UdareRoot = Join-Path `
    $DataRoot `
    "udare_store\$WorkspaceId"

$UdareMetadataRoot = Join-Path `
    $UdareRoot `
    "metadata"

$UdareManifestPath = Join-Path `
    $UdareRoot `
    "manifests\udare_store_manifest.json"

function Normalize-Url {
    param(
        [string]$Url
    )

    if ([string]::IsNullOrWhiteSpace($Url)) {
        return $null
    }

    return $Url.Trim().TrimEnd("/").ToLowerInvariant()
}

function Get-JsonValuesRecursive {
    param(
        [object]$Value,
        [System.Collections.Generic.List[string]]$Ids,
        [System.Collections.Generic.List[string]]$Urls
    )

    if ($null -eq $Value) {
        return
    }

    if ($Value -is [string]) {
        $Text = [string]$Value

        foreach (
            $Match in [regex]::Matches(
                $Text,
                'raw_html_[0-9a-fA-F]{8,}'
            )
        ) {
            $Ids.Add($Match.Value.ToLowerInvariant())
        }

        if (
            $Text -match '^https?://' -and
            $Text.Length -lt 4096
        ) {
            $Normalized = Normalize-Url $Text

            if ($null -ne $Normalized) {
                $Urls.Add($Normalized)
            }
        }

        return
    }

    if (
        $Value -is [System.Collections.IDictionary]
    ) {
        foreach ($Key in $Value.Keys) {
            Get-JsonValuesRecursive `
                -Value $Value[$Key] `
                -Ids $Ids `
                -Urls $Urls
        }

        return
    }

    if (
        $Value -is [System.Collections.IEnumerable] -and
        -not ($Value -is [string])
    ) {
        foreach ($Item in $Value) {
            Get-JsonValuesRecursive `
                -Value $Item `
                -Ids $Ids `
                -Urls $Urls
        }

        return
    }

    foreach ($Property in $Value.PSObject.Properties) {
        Get-JsonValuesRecursive `
            -Value $Property.Value `
            -Ids $Ids `
            -Urls $Urls
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "UDARE MISSING-THREE DIAGNOSIS V2"
Write-Host "============================================================"
Write-Host "Workspace: $WorkspaceId"

# ============================================================
# 1. VERIFY UDARE
# ============================================================

Write-Host ""
Write-Host "1. UDARE STORE"

if (-not (Test-Path $UdareManifestPath)) {
    throw "UDARE manifest not found: $UdareManifestPath"
}

if (-not (Test-Path $UdareMetadataRoot)) {
    throw "UDARE metadata directory not found: $UdareMetadataRoot"
}

$Manifest = Get-Content `
    -Path $UdareManifestPath `
    -Raw `
    -Encoding utf8 |
    ConvertFrom-Json

$UdareMetadataFiles = @(
    Get-ChildItem `
        -Path $UdareMetadataRoot `
        -Filter "*.json" `
        -File
)

$UdareIds = @(
    foreach ($File in $UdareMetadataFiles) {
        $Matches = [regex]::Matches(
            $File.BaseName,
            'raw_html_[0-9a-fA-F]{8,}'
        )

        foreach ($Match in $Matches) {
            $Match.Value.ToLowerInvariant()
        }

        try {
            $Text = Get-Content `
                -Path $File.FullName `
                -Raw `
                -Encoding utf8

            foreach (
                $Match in [regex]::Matches(
                    $Text,
                    'raw_html_[0-9a-fA-F]{8,}'
                )
            ) {
                $Match.Value.ToLowerInvariant()
            }
        }
        catch {
            Write-Host "Unreadable UDARE metadata: $($File.FullName)"
        }
    }
) | Sort-Object -Unique

$UdareUrls = @(
    foreach ($File in $UdareMetadataFiles) {
        try {
            $Json = Get-Content `
                -Path $File.FullName `
                -Raw `
                -Encoding utf8 |
                ConvertFrom-Json

            $CandidateProperties = @(
                "source_url",
                "canonical_url",
                "url",
                "page_url",
                "requested_url",
                "final_url"
            )

            foreach ($Name in $CandidateProperties) {
                $Property = $Json.PSObject.Properties[$Name]

                if (
                    $null -ne $Property -and
                    -not [string]::IsNullOrWhiteSpace(
                        [string]$Property.Value
                    )
                ) {
                    Normalize-Url ([string]$Property.Value)
                }
            }
        }
        catch {
            # The ID comparison remains available.
        }
    }
) |
Where-Object {
    -not [string]::IsNullOrWhiteSpace($_)
} |
Sort-Object -Unique

Write-Host "Manifest records:       $($Manifest.record_count)"
Write-Host "Metadata files:         $($UdareMetadataFiles.Count)"
Write-Host "Unique UDARE IDs:       $($UdareIds.Count)"
Write-Host "Unique UDARE URLs:      $($UdareUrls.Count)"

# ============================================================
# 2. DISCOVER RAW HTML STORE PATHS
# ============================================================

Write-Host ""
Write-Host "2. RAW HTML STORE DISCOVERY"

$PreferredPaths = @(
    (Join-Path $DataRoot "raw_website_html_store_v1"),
    (Join-Path $DataRoot "raw_website_html_store"),
    (Join-Path $DataRoot "raw_html_store"),
    (Join-Path $DataRoot "website_raw_html_store"),
    (Join-Path $DataRoot "enterprise_raw_html_store")
)

$CandidateRoots = [System.Collections.Generic.List[string]]::new()

foreach ($Path in $PreferredPaths) {
    if (Test-Path $Path) {
        $CandidateRoots.Add(
            (Resolve-Path $Path).Path
        )
    }
}

$DiscoveredPaths = @(
    Get-ChildItem `
        -Path $DataRoot `
        -Recurse `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match (
            'raw_website_html_store|' +
            'raw_html_store|' +
            'website_raw_html|' +
            'raw_website_html'
        )
    }
)

foreach ($Item in $DiscoveredPaths) {
    if ($Item.PSIsContainer) {
        $CandidateRoots.Add($Item.FullName)
    }
    else {
        $CandidateRoots.Add($Item.DirectoryName)
    }
}

$CandidateRoots = @(
    $CandidateRoots |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    Sort-Object -Unique
)

Write-Host "Candidate roots:        $($CandidateRoots.Count)"

foreach ($Root in $CandidateRoots) {
    Write-Host "  $Root"
}

if ($CandidateRoots.Count -eq 0) {
    Write-Host ""
    Write-Host "No named Raw HTML Store path was found."
    Write-Host "Running fallback raw_html identity search under data..."

    $FallbackMatches = @(
        Get-ChildItem `
            -Path $DataRoot `
            -File `
            -Recurse `
            -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match 'raw_html_[0-9a-fA-F]{8,}'
        }
    )

    $CandidateRoots = @(
        $FallbackMatches.DirectoryName |
        Sort-Object -Unique
    )

    Write-Host "Fallback roots:         $($CandidateRoots.Count)"

    foreach ($Root in $CandidateRoots) {
        Write-Host "  $Root"
    }
}

if ($CandidateRoots.Count -eq 0) {
    Write-Host ""
    Write-Host "RESULT: RAW HTML STORE STILL NOT LOCATED"
    Write-Host "No files were modified."
    exit 1
}

# ============================================================
# 3. COLLECT RAW STORE FILES
# ============================================================

Write-Host ""
Write-Host "3. RAW HTML STORE FILE COLLECTION"

$RawFiles = @(
    foreach ($Root in $CandidateRoots) {
        Get-ChildItem `
            -Path $Root `
            -File `
            -Recurse `
            -ErrorAction SilentlyContinue
    }
) |
Sort-Object FullName -Unique

Write-Host "Files inspected:        $($RawFiles.Count)"

$ExtensionSummary = @(
    $RawFiles |
    Group-Object Extension |
    Sort-Object Count -Descending
)

foreach ($Group in $ExtensionSummary) {
    $Extension = $Group.Name

    if ([string]::IsNullOrWhiteSpace($Extension)) {
        $Extension = "[no extension]"
    }

    Write-Host (
        "  {0,-15} {1}" -f `
            $Extension,
            $Group.Count
    )
}

# ============================================================
# 4. EXTRACT RAW IDENTITIES
# ============================================================

Write-Host ""
Write-Host "4. RAW HTML IDENTITIES"

$RawIdsList = [System.Collections.Generic.List[string]]::new()
$RawUrlsList = [System.Collections.Generic.List[string]]::new()

$RawIdEvidence = [System.Collections.Generic.List[object]]::new()

foreach ($File in $RawFiles) {
    $FileIds = [System.Collections.Generic.HashSet[string]]::new()

    foreach (
        $Match in [regex]::Matches(
            $File.Name,
            'raw_html_[0-9a-fA-F]{8,}'
        )
    ) {
        $Id = $Match.Value.ToLowerInvariant()

        $RawIdsList.Add($Id)
        $FileIds.Add($Id) | Out-Null
    }

    if (
        $File.Extension -in @(
            ".json",
            ".jsonl",
            ".txt",
            ".html",
            ".htm",
            ".csv"
        )
    ) {
        try {
            $Text = Get-Content `
                -Path $File.FullName `
                -Raw `
                -Encoding utf8

            foreach (
                $Match in [regex]::Matches(
                    $Text,
                    'raw_html_[0-9a-fA-F]{8,}'
                )
            ) {
                $Id = $Match.Value.ToLowerInvariant()

                $RawIdsList.Add($Id)
                $FileIds.Add($Id) | Out-Null
            }

            foreach (
                $Match in [regex]::Matches(
                    $Text,
                    'https?://[^"''<>\s\\]+'
                )
            ) {
                $Url = Normalize-Url $Match.Value

                if ($null -ne $Url) {
                    $RawUrlsList.Add($Url)
                }
            }

            if ($File.Extension -eq ".json") {
                try {
                    $Json = $Text | ConvertFrom-Json

                    Get-JsonValuesRecursive `
                        -Value $Json `
                        -Ids $RawIdsList `
                        -Urls $RawUrlsList
                }
                catch {
                    # Some files may be JSONL or unrelated JSON.
                }
            }
        }
        catch {
            Write-Host "Unreadable raw file: $($File.FullName)"
        }
    }

    foreach ($Id in $FileIds) {
        $RawIdEvidence.Add(
            [PSCustomObject]@{
                source_record_id = $Id
                file_path        = $File.FullName
            }
        )
    }
}

$RawIds = @(
    $RawIdsList |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    Sort-Object -Unique
)

$RawUrls = @(
    $RawUrlsList |
    Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } |
    Sort-Object -Unique
)

Write-Host "Unique raw IDs:         $($RawIds.Count)"
Write-Host "Unique raw URLs:        $($RawUrls.Count)"

# ============================================================
# 5. COMPARE RAW STORE TO UDARE STORE
# ============================================================

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

Write-Host "Missing source IDs:     $($MissingIds.Count)"

foreach ($Id in $MissingIds) {
    Write-Host ""
    Write-Host "MISSING SOURCE ID: $Id"

    $Evidence = @(
        $RawIdEvidence |
        Where-Object {
            $_.source_record_id -eq $Id
        } |
        Select-Object -ExpandProperty file_path -Unique
    )

    if ($Evidence.Count -eq 0) {
        Write-Host "  Evidence file not resolved."
    }
    else {
        foreach ($Path in ($Evidence | Select-Object -First 10)) {
            Write-Host "  $Path"
        }
    }
}

Write-Host ""
Write-Host "Raw URLs absent from UDARE: $($MissingUrls.Count)"

foreach ($Url in ($MissingUrls | Select-Object -First 20)) {
    Write-Host "  $Url"
}

# ============================================================
# 6. FINAL COUNT ASSESSMENT
# ============================================================

Write-Host ""
Write-Host "6. COUNT ASSESSMENT"

Write-Host "Expected Raw HTML:      2225"
Write-Host "Raw IDs discovered:     $($RawIds.Count)"
Write-Host "UDARE IDs discovered:   $($UdareIds.Count)"
Write-Host "Missing UDARE IDs:      $($MissingIds.Count)"

if (
    $RawIds.Count -eq 2225 -and
    $UdareIds.Count -eq 2222 -and
    $MissingIds.Count -eq 3
) {
    Write-Host "Missing-three diagnosis: PASS"
}
else {
    Write-Host "Missing-three diagnosis: NEEDS REVIEW"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "DIAGNOSIS COMPLETE — READ ONLY"
Write-Host "NO UDARE OR RAW HTML FILES WERE MODIFIED"
Write-Host "============================================================"
