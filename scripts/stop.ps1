param([switch]$DockerServices)
. (Join-Path $PSScriptRoot 'common.ps1')
$record = Join-Path $script:Root '.runtime\api.json'
if (Test-Path -LiteralPath $record) {
    $saved = Get-Content -LiteralPath $record -Raw | ConvertFrom-Json
    $process = Get-Process -Id $saved.pid -ErrorAction SilentlyContinue
    if ($process) {
        $command = Get-CimInstance Win32_Process -Filter "ProcessId=$($saved.pid)"
        $sameStart = $process.StartTime.ToUniversalTime() -eq ([datetime]$saved.started).ToUniversalTime()
        if (-not $sameStart -or $command.CommandLine -notlike '*scripts*run_api.py*' -or $command.CommandLine -notlike "*$script:Root*") {
            throw 'PID ownership check failed; leaving the process running.'
        }
        if (-not $saved.stop_key) { throw 'No graceful-shutdown key. Stop this older launcher manually.' }
        $signalPath = Join-Path $script:Root ".runtime\stop-$($saved.pid).signal"
        Set-Content -LiteralPath $signalPath -Value $saved.stop_key -Encoding Ascii -NoNewline
        if (-not $process.WaitForExit(45000)) { throw 'Graceful shutdown timed out; inspect API logs. No forced termination was performed.' }
        Write-Host 'Gracefully stopped the API process started by this checkout. Data files are retained.'
    }
    Remove-Item -LiteralPath $record
} else { Write-Host 'No owned API PID record; existing/manual API processes are left running.' }
if ($DockerServices) {
    & docker compose -f $script:Compose stop
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose stop failed.' }
}
