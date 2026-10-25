param([string]$Message = "What is included in routine AC maintenance?", [switch]$TestMode)
. (Join-Path $PSScriptRoot 'common.ps1')
$config = Get-ProjectSettings
$url = if ($TestMode) { $config.webhook -replace '/webhook/', '/webhook-test/' } else { $config.webhook }
$body = @{ message = $Message } | ConvertTo-Json
Write-Host "POST $url"
Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $body -TimeoutSec 190 | ConvertTo-Json -Depth 10
