# scripts/test_preview.ps1

# 1) Create a clean UTF-8 (no BOM) test file
$testPath = Join-Path $PWD "wrap_test.txt"
[System.IO.File]::WriteAllText(
  $testPath,
  "stored via api upload`r`n",
  [System.Text.UTF8Encoding]::new($false)   # no BOM
)

# 2) Upload and save response
$uploadUrl = "http://127.0.0.1:8001/api/files/upload?workspace_id=default"
curl.exe -s -F "file=@$testPath" $uploadUrl -o upload.json

# 3) Read upload.json and extract doc_id safely
$uploadObj = Get-Content .\upload.json -Raw | ConvertFrom-Json

if (-not $uploadObj.ok) {
  Write-Host "UPLOAD FAILED:" -ForegroundColor Red
  Write-Host (Get-Content .\upload.json -Raw)
  exit 1
}

$docId = $uploadObj.doc.doc_id
if (-not $docId) {
  Write-Host "UPLOAD RESPONSE MISSING doc.doc_id:" -ForegroundColor Red
  Write-Host (Get-Content .\upload.json -Raw)
  exit 1
}

Write-Host "doc_id:" $docId

# 4) Preview and save response
$previewUrl = "http://127.0.0.1:8001/api/files/preview?workspace_id=default&doc_id=$docId"
curl.exe -s $previewUrl -o preview.json

# 5) Print preview outputs safely
$previewObj = Get-Content .\preview.json -Raw | ConvertFrom-Json

if (-not $previewObj.ok) {
  Write-Host "PREVIEW FAILED:" -ForegroundColor Red
  Write-Host (Get-Content .\preview.json -Raw)
  exit 1
}

Write-Host "`n--- text ---"
$previewObj.text

Write-Host "`n--- html ---"
$previewObj.html
