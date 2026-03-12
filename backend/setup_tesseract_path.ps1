param(
    [switch]$PersistMachine
)

$ErrorActionPreference = 'Stop'

function Get-TesseractExe {
    $resolved = Get-Command tesseract -ErrorAction SilentlyContinue
    if ($resolved -and $resolved.Source) {
        return $resolved.Source
    }

    $candidates = @(
        'C:\Program Files\Tesseract-OCR\tesseract.exe',
        'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        [System.IO.Path]::Combine($env:LOCALAPPDATA, 'Programs\Tesseract-OCR\tesseract.exe')
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Add-ToPathIfMissing {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetDir,
        [ValidateSet('User','Machine')]
        [string]$Scope
    )

    $current = [Environment]::GetEnvironmentVariable('Path', $Scope)
    $parts = @()

    if ([string]::IsNullOrWhiteSpace($current) -eq $false) {
        $parts = $current.Split(';') | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    }

    $alreadyPresent = $parts | Where-Object { $_.TrimEnd('\\') -ieq $TargetDir.TrimEnd('\\') }
    if ($alreadyPresent) {
        Write-Host "[OK] PATH $Scope ya contiene: $TargetDir"
        return
    }

    $newPath = if ([string]::IsNullOrWhiteSpace($current)) { $TargetDir } else { "$current;$TargetDir" }
    [Environment]::SetEnvironmentVariable('Path', $newPath, $Scope)
    Write-Host "[OK] Anadido a PATH ${Scope}: $TargetDir"
}

$tesseractExe = Get-TesseractExe
if (-not $tesseractExe) {
    Write-Error 'No se encontro tesseract.exe. Instala Tesseract OCR primero.'
    exit 1
}

$tesseractDir = Split-Path $tesseractExe -Parent
Write-Host "[INFO] Tesseract detectado en: $tesseractExe"

# Persistente para el usuario actual
Add-ToPathIfMissing -TargetDir $tesseractDir -Scope User

# Opcional: persistente a nivel de sistema (requiere PowerShell como administrador)
if ($PersistMachine) {
    try {
        Add-ToPathIfMissing -TargetDir $tesseractDir -Scope Machine
    }
    catch {
        Write-Warning 'No se pudo escribir PATH Machine. Ejecuta PowerShell como administrador para usar -PersistMachine.'
    }
}

# Disponible de inmediato en esta sesion
if (($env:Path.Split(';') | ForEach-Object { $_.Trim() }) -notcontains $tesseractDir) {
    $env:Path = "$tesseractDir;$env:Path"
}

# Ayuda explicita para librerias Python/otras herramientas
$env:TESSERACT_CMD = $tesseractExe

Write-Host "[INFO] PATH actual incluye Tesseract: $tesseractDir"
Write-Host "[INFO] TESSERACT_CMD: $env:TESSERACT_CMD"
Write-Host ''

Write-Host '[CHECK] where tesseract'
where.exe tesseract

Write-Host '[CHECK] tesseract --version'
& $tesseractExe --version

Write-Host '[CHECK] tesseract --list-langs'
& $tesseractExe --list-langs

Write-Host ''
Write-Host '[DONE] Reinicia VS Code o abre una nueva terminal para heredar el PATH persistente.'
