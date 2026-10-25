$ErrorActionPreference = 'Stop'
$script:Root = Split-Path -Parent $PSScriptRoot
$script:Python = Join-Path $script:Root '.venv\Scripts\python.exe'
$script:Compose = Join-Path $script:Root 'docker\compose.yaml'

function Assert-Python {
    if (-not (Test-Path -LiteralPath $script:Python)) { throw 'Run scripts/setup.ps1 first.' }
}

function Invoke-Python {
    & $script:Python @args
    if ($LASTEXITCODE -ne 0) { throw "Python exited with code $LASTEXITCODE" }
}

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try { $client.Connect('127.0.0.1', $Port); return $true }
    catch { return $false }
    finally { $client.Dispose() }
}

function Get-ProjectSettings {
    Assert-Python
    Push-Location $script:Root
    try {
        $raw = & $script:Python -c 'import json; from service.config import settings; print(json.dumps({"token":settings.workflow_token,"webhook":settings.n8n_webhook_url}))'
        if ($LASTEXITCODE -ne 0) { throw 'Cannot load project configuration.' }
        return ($raw | ConvertFrom-Json)
    } finally { Pop-Location }
}
