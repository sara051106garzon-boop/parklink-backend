#requires -Version 5.1
<#
.SYNOPSIS
    Carga los 8 secrets de despliegue de ParkLink en los GitHub Environments
    "staging" y "production" del repositorio parklink-backend.

.DESCRIPTION
    - No pide pegar bloques largos: la llave privada se lee del archivo y se
      envia por stdin a `gh secret set`.
    - Es idempotente: si existe un respaldo local en
      %USERPROFILE%\.parklink\secrets-<entorno>.env reutiliza esos valores;
      si no, genera SECRET_KEY, JWT_SECRET_KEY y la clave de MySQL (base64 de
      48 bytes). La DATABASE_URL generada apunta al servicio "db" del
      docker-compose (BD aislada por entorno).
    - Nunca imprime valores secretos en pantalla.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\cargar-secrets.ps1 -Entornos staging -RotarClaves
#>
param(
    [ValidateSet('staging', 'production')]
    [string[]]$Entornos = @('staging', 'production'),

    [string]$KeyPath = (Join-Path $env:USERPROFILE 'parklink-key.pem'),

    [string]$Repo = 'sara051106garzon-boop/parklink-backend',

    [string]$Gh = 'C:\Program Files\GitHub CLI\gh.exe',

    # Fuerza la regeneracion de SECRET_KEY y JWT_SECRET_KEY.
    [switch]$RotarClaves
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Gh)) {
    $cmd = Get-Command gh.exe -ErrorAction SilentlyContinue
    if ($cmd) { $Gh = $cmd.Source } else { throw "No se encontro gh.exe. Instala GitHub CLI o pasa -Gh <ruta>." }
}
if (-not (Test-Path $KeyPath)) { throw "No existe la llave privada: $KeyPath" }

# Valida que la llave sea parseable antes de subirla.
$null = & ssh-keygen -y -f $KeyPath 2>&1
if ($LASTEXITCODE -ne 0) { throw "La llave $KeyPath no es una llave privada valida." }

$privateKey = [IO.File]::ReadAllText($KeyPath) -replace "`r`n", "`n"
$backupDir  = Join-Path $env:USERPROFILE '.parklink'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$rng = [Security.Cryptography.RandomNumberGenerator]::Create()
function New-RandomSecret([int]$bytes = 48) {
    $buffer = New-Object byte[] $bytes
    $rng.GetBytes($buffer)
    [Convert]::ToBase64String($buffer)
}
# Clave de MySQL: solo [A-Za-z0-9], para que quepa sin escapar dentro de la
# DATABASE_URL (sin ':', '@', '/' ni '%').
function New-DbPassword([int]$largo = 32) {
    $chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    $buffer = New-Object byte[] $largo
    $rng.GetBytes($buffer)
    -join ($buffer | ForEach-Object { $chars[$_ % $chars.Length] })
}

# Valores no sensibles por entorno. DATABASE_URL se resuelve mas abajo:
# apunta siempre al servicio "db" del compose, con una clave aleatoria.
$config = @{
    staging = [ordered]@{
        EC2_HOST     = '3.138.221.70'
        EC2_USER     = 'ubuntu'
        APP_PORT     = '8000'
        DEPLOY_PATH  = '/home/ubuntu/parklink-staging'
    }
    production = [ordered]@{
        EC2_HOST     = '3.138.221.70'
        EC2_USER     = 'ubuntu'
        APP_PORT     = '8001'
        DEPLOY_PATH  = '/home/ubuntu/parklink-production'
    }
}

foreach ($entorno in $Entornos) {
    Write-Host "== $entorno ==" -ForegroundColor Cyan
    $valores = [ordered]@{}
    foreach ($clave in $config[$entorno].Keys) { $valores[$clave] = $config[$entorno][$clave] }

    # Reutiliza claves previas del respaldo local, salvo que se pida rotarlas.
    $respaldo = Join-Path $backupDir "secrets-$entorno.env"
    $previas = @{}
    if ((Test-Path $respaldo) -and -not $RotarClaves) {
        Get-Content $respaldo | ForEach-Object {
            if ($_ -match '^(?<k>[A-Z_]+)=(?<v>.*)$') { $previas[$matches.k] = $matches.v }
        }
    }
    foreach ($clave in @('SECRET_KEY', 'JWT_SECRET_KEY')) {
        if ($previas.ContainsKey($clave) -and $previas[$clave]) { $valores[$clave] = $previas[$clave] }
        else { $valores[$clave] = New-RandomSecret 48 }
    }
    # DATABASE_URL: se reutiliza la del respaldo si apunta al MySQL del compose;
    # si no (placeholder o host externo sin credenciales), se genera una nueva
    # con clave aleatoria y host "db" (servicio interno del docker-compose).
    $urlPrevia = $previas['DATABASE_URL']
    if ($urlPrevia -and $urlPrevia -match '@db:[0-9]+/' -and $urlPrevia -notmatch 'CAMBIAR|USUARIO_REAL|HOST_REAL') {
        $valores['DATABASE_URL'] = $urlPrevia
    }
    else {
        $valores['DATABASE_URL'] = "mysql+pymysql://parklink:$(New-DbPassword 32)@db:3306/parklink_$entorno"
    }

    foreach ($clave in $valores.Keys) {
        $valores[$clave] | & $Gh secret set $clave --env $entorno --repo $Repo
        if ($LASTEXITCODE -ne 0) { throw "Fallo al definir $clave en $entorno" }
        Write-Host ("  {0,-14} OK" -f $clave)
    }

    # La llave privada va por stdin: nunca aparece en la linea de comandos.
    $privateKey | & $Gh secret set EC2_SSH_KEY --env $entorno --repo $Repo
    if ($LASTEXITCODE -ne 0) { throw "Fallo al definir EC2_SSH_KEY en $entorno" }
    Write-Host ("  {0,-14} OK (stdin, {1} bytes)" -f 'EC2_SSH_KEY', $privateKey.Length)

    $lineas = foreach ($clave in $valores.Keys) { "$clave=$($valores[$clave])" }
    $lineas += "EC2_SSH_KEY_FILE=$KeyPath"
    [IO.File]::WriteAllText($respaldo, (($lineas -join "`n") + "`n"), (New-Object System.Text.UTF8Encoding($false)))
    & icacls $respaldo /inheritance:r /grant:r "$($env:COMPUTERNAME)\$($env:USERNAME):F" | Out-Null
    Write-Host "  respaldo local: $respaldo"
}

Write-Host ''
Write-Host 'Verificacion:' -ForegroundColor Cyan
foreach ($entorno in $Entornos) {
    Write-Host "-- $entorno --"
    & $Gh secret list --env $entorno --repo $Repo
}
