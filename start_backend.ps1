param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$Reload,
    [switch]$InstallDeps
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$EnvExample = Join-Path $ProjectRoot ".env.example"
$EnvFile = Join-Path $ProjectRoot ".env"

if (!(Test-Path $VenvPython)) {
    throw "Virtual environment not found at '$VenvPython'. Please create it first."
}

if (!(Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "Created .env from .env.example"
}

if ($InstallDeps) {
    Write-Host "Installing/updating dependencies in venv..."
    & $VenvPython -m pip install --upgrade -r $Requirements
}

Write-Host "Using interpreter: $VenvPython"
Write-Host "Starting server on http://$Host`:$Port"

$Args = @("-m", "uvicorn", "backend.main:app", "--host", $Host, "--port", "$Port")
if ($Reload) {
    $Args += "--reload"
}

& $VenvPython @Args
