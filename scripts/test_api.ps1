param([string]$Message = "What is included in routine AC maintenance?")
. (Join-Path $PSScriptRoot 'common.ps1')
$config = Get-ProjectSettings
$body = @{ message = $Message } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8003/api/process" -Method Post -Headers @{ "X-Demo-Token" = $config.token } -ContentType "application/json" -Body $body -TimeoutSec 190 | ConvertTo-Json -Depth 10
