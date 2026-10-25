param([switch]$SkipLaya, [switch]$WithUI)
. (Join-Path $PSScriptRoot 'common.ps1')
Push-Location $script:Root
try {
    if (-not (Test-Path -LiteralPath $script:Python)) {
        & py -3.12 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 (64-bit) with the py launcher.' }
    }
    Invoke-Python -m pip install --upgrade pip
    Invoke-Python -m pip install -r requirements.txt -r requirements-dev.txt
    if (-not $SkipLaya) { Invoke-Python -m pip install -r requirements-laya.txt }
    if ($WithUI) { Invoke-Python -m pip install -r requirements-ui.txt }
    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
        Invoke-Python -c "from pathlib import Path; import secrets; p=Path('.env'); p.write_text(p.read_text().replace('local-dev-only-change-me',secrets.token_urlsafe(32)),encoding='utf-8')"
    }
    Write-Host 'Environment ready. Read .env locally; configure the same token in n8n Header Auth.'
    Write-Host 'Next: start Docker/Ollama, run scripts/seed.ps1, then scripts/start.ps1.'
} finally { Pop-Location }
