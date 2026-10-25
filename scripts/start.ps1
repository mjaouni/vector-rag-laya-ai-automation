param([switch]$DockerServices, [switch]$OpenBrowser, [ValidateRange(1024,65535)][int]$Port = 8003)
. (Join-Path $PSScriptRoot 'common.ps1')
Assert-Python
if (-not (Test-Path -LiteralPath (Join-Path $script:Root '.env'))) { throw 'Run scripts/setup.ps1 first.' }
if ($DockerServices) {
    foreach ($entry in @(@{Name='n8n';Ports=@(5678)}, @{Name='mailpit';Ports=@(8025,1025)})) {
        $used = @($entry.Ports | Where-Object { Test-Port $_ })
        if ($used.Count -eq $entry.Ports.Count) {
            Write-Host "$($entry.Name) ports are already active; reusing existing services."
        } elseif ($used.Count -gt 0) {
            throw "Some $($entry.Name) ports are occupied. Inspect docker ps before starting services."
        } else {
            & docker compose -f $script:Compose up -d $entry.Name
            if ($LASTEXITCODE -ne 0) { throw 'Docker Compose startup failed.' }
        }
    }
}
if (Test-Port $Port) {
    $health = Invoke-RestMethod "http://127.0.0.1:$Port/healthz" -TimeoutSec 5
    if ($health.service -ne 'vector-rag-laya') { throw "Port $Port belongs to a different service." }
    Write-Host 'Existing FastAPI is healthy; no duplicate process started.'
    if ($OpenBrowser) { Start-Process "http://localhost:$Port" }
    return
}
Push-Location $script:Root
try {
    Invoke-Python scripts/doctor.py --require-model
    New-Item -ItemType Directory -Force -Path '.runtime' | Out-Null
    $runner = Join-Path $PSScriptRoot 'run_api.py'
    $server = Start-Process -FilePath $script:Python -ArgumentList @(('"' + $runner + '"'), '--port', $Port) -WorkingDirectory $script:Root -WindowStyle Hidden -PassThru -RedirectStandardOutput '.runtime/api.stdout.log' -RedirectStandardError '.runtime/api.stderr.log'
    $ready = $false
    for ($attempt=0; $attempt -lt 30; $attempt++) {
        if ($server.HasExited) { throw 'API exited. Read .runtime/api.stderr.log.' }
        try { $health=Invoke-RestMethod "http://127.0.0.1:$Port/healthz" -TimeoutSec 2; $ready=$health.service -eq 'vector-rag-laya' } catch {}
        if ($ready) { break }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'API readiness timed out. Inspect .runtime logs.' }
    $owner = Get-Content -LiteralPath '.runtime/api.json' -Raw | ConvertFrom-Json
    $worker = Get-Process -Id $owner.pid
    @{pid=$worker.Id;started=$worker.StartTime.ToUniversalTime().ToString('o');port=$Port;stop_key=$owner.stop_key} | ConvertTo-Json | Set-Content -LiteralPath '.runtime/api.json'
    Write-Host "FastAPI ready at http://localhost:$Port. Restrict this port with Windows Firewall."
    if ($OpenBrowser) { Start-Process "http://localhost:$Port" }
} finally { Pop-Location }
