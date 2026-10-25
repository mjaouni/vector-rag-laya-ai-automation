. (Join-Path $PSScriptRoot 'common.ps1')
Assert-Python
if (Test-Port 8003) { throw 'Port 8003 is active. Stop the API before opening embedded Qdrant.' }
Push-Location $script:Root
try { Invoke-Python cli.py seed }
finally { Pop-Location }
