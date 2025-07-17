-----

# Script de Automatización para SUA (IMSS) 🚀

Este script de PowerShell está diseñado para automatizar y simplificar el proceso de instalación y/o actualización del **Sistema Único de Autodeterminación (SUA)** del IMSS en sistemas Windows.

El objetivo principal es eliminar los errores comunes y reducir el tiempo invertido en este proceso, especialmente al manejar múltiples clientes o instalaciones.

-----

## Características Principales ✨

* **Detección Automática:** Busca inteligentemente si el SUA ya está instalado, sin importar si está en `C:`, `D:`, o cualquier otra unidad.
* **Instalación desde Cero:** Si no detecta una instalación, descarga e inicia la instalación de la versión base del SUA.
* **Actualización Inteligente:** Compara la versión instalada con la última versión disponible (tú la especificas al ejecutar) y decide si se necesita una actualización.
* **Asistente de Ruta:** ¡Soluciona el problema más común\! Copia automáticamente la ruta de instalación correcta al portapapeles, para que solo tengas que pegarla (`Ctrl+V`) en el instalador.
* **Interactivo:** Te pregunta qué versión deseas instalar, haciendo el script reutilizable para futuras actualizaciones sin necesidad de modificar el código.
* **Ejecución Remota:** Diseñado para ser ejecutado con un solo comando directamente desde GitHub.

-----

## Requisitos 📋

* Windows 10 o superior.
* PowerShell 5.1 o superior (viene instalado por defecto en Windows 10).
* Permisos de **Administrador** para poder instalar software.

-----

## ¿Cómo Usar? ⚡

La forma más sencilla de usar este script es ejecutarlo directamente desde internet. No necesitas descargar ningún archivo manualmente.

1. **Abrir PowerShell como Administrador.**

      * Busca "PowerShell" en el menú de inicio, haz clic derecho y selecciona "Ejecutar como administrador".

2. **Establecer la Política de Ejecución (Solo la primera vez por sesión).**

      * Por seguridad, PowerShell bloquea scripts de internet. Ejecuta el siguiente comando para permitirlo solo en esta sesión:

        ```powershell
        Set-ExecutionPolicy RemoteSigned -Scope Process
        ```

3. **Ejecutar el Script desde GitHub.**

      * Usa el siguiente comando, **reemplazando `[TU_USUARIO]` y `[TU_REPOSITORIO]`** con tu nombre de usuario y el nombre de tu repositorio en GitHub.

        ```powershell
        irm "https://raw.githubusercontent.com/[TU_USUARIO]/[TU_REPOSITORIO]/main/ActualizarSUA.ps1" | iex
        ```

-----

## Flujo de Trabajo del Script ⚙️

Una vez ejecutado, el script te guiará por los siguientes pasos:

1. Te pedirá que **introduzcas el número de la última versión** que deseas instalar (por ejemplo, `3.6.7`).
2. Buscará la instalación actual del SUA.
3. Si es necesario, descargará la versión base o la de actualización.
4. Te avisará con un mensaje en verde que **la ruta de instalación correcta ha sido copiada a tu portapapeles**.
5. Lanzará el instalador oficial del IMSS.
6. Cuando el instalador te pida la ruta, simplemente haz clic en el campo de texto y presiona **`Ctrl + V`** para pegar la ruta correcta y continúa con la instalación.

-----

## Contribuciones

Si encuentras un error o tienes una sugerencia para mejorar el script, por favor abre un "Issue" en este repositorio.

-----

## Descargo de Responsabilidad

Este script es una herramienta de automatización no oficial y no está afiliada, mantenida ni respaldada por el IMSS. Es proporcionada "tal cual" y debes usarla bajo tu propio riesgo. El autor no se hace responsable de cualquier posible pérdida de datos o daño al sistema. Siempre se recomienda tener respaldos de la información antes de realizar cualquier actualización.
