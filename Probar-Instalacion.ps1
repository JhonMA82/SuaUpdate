<#
.SYNOPSIS
    Automatiza la instalación y/o actualización del Sistema Único de Autodeterminación (SUA) del IMSS.

.NOTES
    Versión: 1.2 - Añadida funcionalidad para copiar la ruta de instalación al portapapeles.
#>

#region --- CONFIGURACIÓN ---
$ultimaVersionString = "3.6.6"
$urlBaseInstalador = "https://www.imss.gob.mx/sites/all/statics/pdf/sua/InstaladorSUA353.exe"
$versionSinPuntos = $ultimaVersionString.Replace('.', '')
$urlActualizador = "https://www.imss.gob.mx/sites/all/statics/pdf/sua/VersionSUA$($versionSinPuntos).exe"
$directorioDescargas = Join-Path $env:TEMP "SUA_Instaladores"
#endregion

#region --- FUNCIONES AUXILIARES ---
function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [ValidateSet("INFO", "SUCCESS", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )
    $colorMap = @{
        INFO    = "White"
        SUCCESS = "Green"
        WARN    = "Yellow"
        ERROR   = "Red"
    }
    Write-Host "[$Level] $Message" -ForegroundColor $colorMap[$Level]
}

function Find-SUAInstallation {
    Write-Log "🔍 Buscando instalación existente del SUA..."
    $rutasRegistro = @(
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    foreach ($ruta in $rutasRegistro) {
        $instalacion = Get-ItemProperty $ruta -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*Sistema Único de Autodeterminación*" }
        if ($instalacion) {
            $rutaEncontrada = $instalacion.InstallLocation
            if ($rutaEncontrada -and (Test-Path (Join-Path $rutaEncontrada "SUA.exe"))) {
                Write-Log "✅ Encontrado en el registro: $rutaEncontrada" -Level SUCCESS
                return $rutaEncontrada.TrimEnd('\')
            }
        }
    }
    Write-Log "No se encontró en el registro. Buscando en los discos duros..." -Level WARN
    $drives = Get-PSDrive -PSProvider FileSystem
    foreach ($drive in $drives) {
        $rutaPotencial = Join-Path $drive.Root "Cobranza\SUA"
        if (Test-Path (Join-Path $rutaPotencial "SUA.exe")) {
            Write-Log "✅ Encontrado en el disco: $rutaPotencial" -Level SUCCESS
            return $rutaPotencial
        }
    }
    Write-Log "No se encontró ninguna instalación del SUA." -Level ERROR
    return $null
}

function Download-File {
    param(
        [string]$Url,
        [string]$DestinationPath
    )
    $ParentDirectory = Split-Path -Path $DestinationPath -Parent
    if (-not (Test-Path -Path $ParentDirectory)) {
        Write-Log "📂 Creando directorio de descargas en: $ParentDirectory"
        New-Item -ItemType Directory -Path $ParentDirectory -Force | Out-Null
    }
    Write-Log "⬇️  Descargando desde $Url..."
    try {
        Invoke-WebRequest -Uri $Url -OutFile $DestinationPath -UseBasicParsing
        Write-Log "✔️  Descarga completa en: $DestinationPath" -Level SUCCESS
        return $true
    }
    catch {
        Write-Log "❌ Error al descargar el archivo. Verifica la URL y tu conexión a internet." -Level ERROR
        Write-Log $_.Exception.Message -Level ERROR
        return $false
    }
}
#endregion

#region --- SCRIPT PRINCIPAL ---
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Log "Este script requiere privilegios de Administrador. Por favor, haz clic derecho y 'Ejecutar como Administrador'." -Level ERROR
    Read-Host "Presiona Enter para salir."
    exit
}

Clear-Host
Write-Log "🚀 INICIO DEL SCRIPT DE INSTALACIÓN/ACTUALIZACIÓN DE SUA 🚀"
Write-Log "=========================================================="

$rutaInstalacion = Find-SUAInstallation

if (-not $rutaInstalacion) {
    Write-Log "Se procederá con una instalación nueva del SUA." -Level INFO
    $baseInstallerPath = Join-Path $directorioDescargas "InstaladorSUA353.exe"
    
    if (Download-File -Url $urlBaseInstalador -DestinationPath $baseInstallerPath) {
        Write-Log "▶️  Iniciando instalador base. Por favor, completa la instalación manualmente." -Level WARN
        Write-Log "El script continuará para intentar actualizar después de que cierres el instalador."
        Start-Process -FilePath $baseInstallerPath -Wait
        
        Write-Log "Instalación base finalizada. Buscando de nuevo la ruta para actualizar..."
        $rutaInstalacion = Find-SUAInstallation
        if (-not $rutaInstalacion) {
            Write-Log "No se pudo encontrar la ruta de instalación después de ejecutar el instalador. El script no puede continuar." -Level ERROR
            Read-Host "Presiona Enter para salir."
            exit
        }
    }
    else {
        Read-Host "Presiona Enter para salir."
        exit
    }
}

Write-Log "Verificando la versión instalada en: $rutaInstalacion"
try {
    $versionInfo = (Get-Item -Path (Join-Path $rutaInstalacion "SUA.exe")).VersionInfo
    $versionInstalada = [System.Version]$versionInfo.ProductVersion
    $ultimaVersion = [System.Version]$ultimaVersionString
    
    Write-Log "Versión instalada: $versionInstalada"
    Write-Log "Última versión disponible: $ultimaVersion"
    
    if ($versionInstalada -ge $ultimaVersion) {
        Write-Log "✅ ¡Excelente! El cliente ya tiene la última versión del SUA." -Level SUCCESS
    }
    else {
        Write-Log "Se necesita una actualización." -Level WARN
        $updaterPath = Join-Path $directorioDescargas "VersionSUA$($versionSinPuntos).exe"

        if (Download-File -Url $urlActualizador -DestinationPath $updaterPath) {
            
            # --- INICIO DE LA MODIFICACIÓN ---
            
            # 1. Copiamos la ruta correcta al portapapeles.
            Set-Clipboard -Value $rutaInstalacion
            Write-Log "📋 ¡La ruta correcta '$rutaInstalacion' ha sido copiada a tu portapapeles!" -Level SUCCESS
            
            # 2. Lanzamos el actualizador (sin argumentos, ya que los ignora).
            Write-Log "▶️  Iniciando el actualizador. Cuando te pida la ruta, simplemente presiona Ctrl+V para pegar la correcta." -Level WARN
            Start-Process -FilePath $updaterPath -Wait

            # --- FIN DE LA MODIFICACIÓN ---
            
            # Verificación final
            Clear-Content (Join-Path $rutaInstalacion "SUA.exe") -Stream "Zone.Identifier" -ErrorAction SilentlyContinue
            $versionInfoFinal = (Get-Item -Path (Join-Path $rutaInstalacion "SUA.exe")).VersionInfo
            $versionFinal = [System.Version]$versionInfoFinal.ProductVersion

            if ($versionFinal -ge $ultimaVersion) {
                Write-Log "🎉 ¡Actualización completada exitosamente a la versión $versionFinal!" -Level SUCCESS
            }
            else {
                Write-Log "La actualización se ejecutó, pero la versión no parece haber cambiado. Revisa manualmente." -Level ERROR
                Write-Log "Versión actual después del intento: $versionFinal"
            }
        }
    }
}
catch {
    Write-Log "❌ Ocurrió un error al verificar la versión del archivo SUA.exe. ¿Está dañado o la ruta es incorrecta?" -Level ERROR
    Write-Log $_.Exception.Message -Level ERROR
}

Write-Log "=========================================================="
Write-Log "SCRIPT FINALIZADO."
Read-Host "Presiona Enter para cerrar esta ventana."
#endregion