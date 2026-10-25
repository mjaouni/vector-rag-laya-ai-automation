. (Join-Path $PSScriptRoot 'common.ps1')
$config = Get-ProjectSettings
$id = 'smtp-check-' + [guid]::NewGuid().ToString('N')
$body = @{request_id=$id;status='answered';answer='Local SMTP delivery check; no customer was contacted.';sources=@('maintenance.md');reason='smtp_delivery_check'} | ConvertTo-Json
$result = Invoke-RestMethod 'http://127.0.0.1:8003/api/notify' -Method Post -Headers @{'X-Demo-Token'=$config.token} -ContentType 'application/json' -Body $body
if (-not $result.notified) { throw 'Notification was not sent.' }
$inbox = Invoke-RestMethod 'http://127.0.0.1:8025/api/v1/messages' -TimeoutSec 10
if (-not ($inbox.messages | Where-Object { $_.Subject -like "*$id*" })) { throw 'Test email not found in the latest Mailpit inbox page.' }
Write-Host "Mailpit received $id. This test verifies SMTP delivery, not RAG inference."
