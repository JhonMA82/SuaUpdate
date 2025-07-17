import os
import subprocess
import requests
import win32api
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.parse
import threading
import time
import string
import glob

# --- ÚNICA PARTE A MODIFICAR EN EL FUTURO ---
# Simplemente cambia este número cuando salga una nueva versión del SUA.
VERSION_A_INSTALAR = "3.6.6"
# ---------------------------------------------

# URL base para descargar SUA cuando no está instalado
URL_INSTALADOR_BASE = "https://www.imss.gob.mx/sites/all/statics/pdf/sua/InstaladorSUA353.exe"

class VentanaProgreso:
    """Ventana con barra de progreso para mostrar descargas e instalaciones."""
    def __init__(self, titulo, mensaje):
        self.root = tk.Tk()
        self.root.title(titulo)
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Etiqueta de mensaje
        self.label = tk.Label(self.root, text=mensaje, wraplength=380, pady=10)
        self.label.pack()
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=350)
        self.progress.pack(pady=10)
        
        # Etiqueta de estado
        self.status = tk.Label(self.root, text="Iniciando...", fg="blue")
        self.status.pack()
        
        # Iniciar animación
        self.progress.start(10)
        
    def actualizar_estado(self, texto):
        """Actualiza el texto de estado."""
        if self.root.winfo_exists():
            self.status.config(text=texto)
            self.root.update()
        
    def cerrar(self):
        """Cierra la ventana."""
        if self.root.winfo_exists():
            self.progress.stop()
            self.root.destroy()
        
    def mostrar(self):
        """Muestra la ventana y ejecuta el loop principal."""
        self.root.mainloop()

def mostrar_mensaje(titulo, mensaje):
    """Muestra una ventana emergente simple."""
    root = tk.Tk()
    root.withdraw()
    try:
        messagebox.showinfo(titulo, mensaje)
    finally:
        root.quit()
        root.destroy()

def obtener_version_archivo(ruta_archivo):
    """Obtiene la versión de un archivo ejecutable."""
    try:
        info = win32api.GetFileVersionInfo(ruta_archivo, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}"
        return version
    except Exception:
        return None

def descargar_archivo(url, ruta_guardado, ventana_progreso=None):
    """Descarga un archivo desde una URL, mostrando el progreso con barra animada."""
    try:
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Conectando al servidor...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        if ventana_progreso:
            if total_size > 0:
                ventana_progreso.progress.stop()
                ventana_progreso.progress.config(mode='determinate', maximum=total_size)
                ventana_progreso.actualizar_estado("Descargando...")
            else:
                ventana_progreso.actualizar_estado("Descargando... (tamaño desconocido)")
        
        downloaded = 0
        with open(ruta_guardado, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if ventana_progreso and total_size > 0:
                        ventana_progreso.progress.config(value=downloaded)
                        percent = (downloaded / total_size) * 100
                        ventana_progreso.actualizar_estado(f"Descargando... {percent:.1f}%")
                        ventana_progreso.root.update()
        
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Descarga completada")
            time.sleep(1)
        
        return True
    except requests.exceptions.RequestException as e:
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Error en la descarga")
            time.sleep(2)
        mostrar_mensaje("Error de Descarga", f"No se pudo descargar el archivo. Verifica tu conexión a internet o que la URL sea correcta.\n\nError: {e}")
        return False

def instalar_actualizacion_silenciosa(ruta_instalador, ventana_progreso=None):
    """Instala el instalador en modo silencioso usando parámetros correctos según el tipo."""
    try:
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Preparando instalación...")
            ventana_progreso.progress.config(mode='indeterminate')
            ventana_progreso.progress.start(10)
        
        # Detectar tipo de instalador
        extension = os.path.splitext(ruta_instalador)[1].lower()
        
        if extension == '.msi':
            # Instalador MSI - usar msiexec con parámetros oficiales
            parametros = ['/i', ruta_instalador, '/quiet', '/norestart']
            proceso = subprocess.Popen(['msiexec'] + parametros, creationflags=subprocess.CREATE_NO_WINDOW)
            
        elif extension == '.exe':
            # Instalador EXE - intentar diferentes métodos silenciosos
            # Método 1: Parámetros estándar de Windows Installer
            parametros = ['/quiet', '/norestart']
            proceso = subprocess.Popen([ruta_instalador] + parametros, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Si falla, intentar otros métodos
            if proceso.wait() != 0:
                # Método 2: Parámetros /S o /s
                proceso = subprocess.Popen([ruta_instalador, '/S'], creationflags=subprocess.CREATE_NO_WINDOW)
                if proceso.wait() != 0:
                    proceso = subprocess.Popen([ruta_instalador, '/s'], creationflags=subprocess.CREATE_NO_WINDOW)
                    if proceso.wait() != 0:
                        # Método 3: Parámetros de InstallShield
                        proceso = subprocess.Popen([ruta_instalador, '/s', '/v"/qn REBOOT=ReallySuppress"'],
                                                 creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Tipo desconocido, intentar /S
            proceso = subprocess.Popen([ruta_instalador, '/S'], creationflags=subprocess.CREATE_NO_WINDOW)
        
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Instalando... esto puede tardar varios minutos")
        
        # Esperar a que termine el proceso
        while proceso.poll() is None:
            if ventana_progreso:
                ventana_progreso.root.update()
            time.sleep(0.5)
        
        if proceso.returncode == 0:
            if ventana_progreso:
                ventana_progreso.actualizar_estado("Instalación completada")
                time.sleep(1)
            return True
        else:
            raise Exception(f"El instalador terminó con código {proceso.returncode}")
            
    except Exception as e:
        if ventana_progreso:
            ventana_progreso.actualizar_estado("Error en la instalación")
            time.sleep(2)
        mostrar_mensaje("Error de Instalación", f"Falló la instalación automática. Se abrirá el instalador para que lo hagas manualmente.\n\nError: {e}")
        os.startfile(ruta_instalador)
        return False

def buscar_sua_en_discos():
    """Busca SUA.exe en todas las unidades de disco disponibles."""
    posibles_rutas = [
        "Cobranza\\SUA\\SUA.exe",
        "Program Files\\Cobranza\\SUA\\SUA.exe",
        "Program Files (x86)\\Cobranza\\SUA\\SUA.exe",
        "SUA\\SUA.exe",
        "IMSS\\SUA\\SUA.exe"
    ]
    
    # Buscar en todas las unidades de disco
    unidades = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    
    for unidad in unidades:
        for ruta_relativa in posibles_rutas:
            ruta_completa = os.path.join(unidad, ruta_relativa)
            if os.path.exists(ruta_completa):
                return ruta_completa
    
    # Buscar con glob en todas las unidades
    for unidad in unidades:
        patrones = [
            os.path.join(unidad, "**", "SUA.exe"),
            os.path.join(unidad, "**", "Cobranza", "SUA", "SUA.exe")
        ]
        for patron in patrones:
            try:
                resultados = glob.glob(patron, recursive=True)
                for resultado in resultados:
                    if "SUA.exe" in resultado and os.path.exists(resultado):
                        return resultado
            except:
                continue
    
    return None

def ejecutar_sua(ruta_sua):
    """Ejecuta el programa SUA."""
    try:
        os.startfile(ruta_sua)
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo iniciar el SUA. Intenta abrirlo manualmente desde su acceso directo.\n\nError: {e}")

def descargar_e_instalar_sua_base():
    """Descarga e instala SUA desde cero cuando no está instalado."""
    try:
        # Guarda el instalador en la carpeta de Descargas del usuario
        ruta_descargas = os.path.join(os.path.expanduser('~'), 'Downloads')
        nombre_archivo_base = "InstaladorSUA353.exe"
        ruta_instalador = os.path.join(ruta_descargas, nombre_archivo_base)
        
        # Crear ventana de progreso
        ventana = VentanaProgreso("Instalación SUA", "El SUA no está instalado.\nDescargando e instalando versión base...")
        
        def proceso_instalacion():
            try:
                if descargar_archivo(URL_INSTALADOR_BASE, ruta_instalador, ventana):
                    if instalar_actualizacion_silenciosa(ruta_instalador, ventana):
                        ventana.actualizar_estado("Instalación completada")
                        time.sleep(1)
                        ventana.cerrar()
                        mostrar_mensaje("¡Instalación Exitosa!", "El SUA se ha instalado correctamente.\n\nA continuación, se iniciará el programa.")
                    else:
                        ventana.cerrar()
                else:
                    ventana.cerrar()
            except Exception as e:
                ventana.cerrar()
                mostrar_mensaje("Error de Instalación", f"Error al intentar instalar SUA:\n\nError: {e}")
        
        # Ejecutar en hilo separado
        threading.Thread(target=proceso_instalacion, daemon=True).start()
        ventana.mostrar()
        
        return True
            
    except Exception as e:
        mostrar_mensaje("Error de Instalación", f"Error al intentar instalar SUA:\n\nError: {e}")
        return False

def main():
    """Función principal para automatizar la actualización del SUA."""
    ruta_sua_exe = r"C:\Cobranza\SUA\SUA.exe"
    
    nombre_archivo_instalador = f"VersionSUA{VERSION_A_INSTALAR.replace('.', '')}.exe"
    url_descarga = f"https://www.imss.gob.mx/sites/all/statics/pdf/sua/{nombre_archivo_instalador}"
    
    # Guarda el instalador en la carpeta de Descargas del usuario
    ruta_descargas = os.path.join(os.path.expanduser('~'), 'Downloads')
    ruta_instalador = os.path.join(ruta_descargas, nombre_archivo_instalador)

    # 1. Buscar SUA en todas las ubicaciones posibles
    ruta_sua_exe = buscar_sua_en_discos()
    
    if not ruta_sua_exe:
        # SUA no está instalado, proceder con instalación base
        if descargar_e_instalar_sua_base():
            # Buscar nuevamente después de la instalación
            ruta_sua_exe = buscar_sua_en_discos()
            if ruta_sua_exe:
                ejecutar_sua(ruta_sua_exe)
            else:
                mostrar_mensaje("Error", "La instalación parece haberse completado, pero no se encontró el ejecutable del SUA.")
        return

    # 2. SUA está instalado, verificar la versión actual
    version_actual = obtener_version_archivo(ruta_sua_exe)
    
    # IMPORTANTE: Si la versión instalada es 3.5.3, forzar actualización a 3.6.6
    if version_actual and (version_actual.startswith(VERSION_A_INSTALAR) or version_actual == "3.5.3"):
        if version_actual == "3.5.3":
            mostrar_mensaje("Actualización Necesaria", f"Tienes la versión {version_actual}.\nSe actualizará a la versión {VERSION_A_INSTALAR}.")
        else:
            mostrar_mensaje("SUA Actualizado", f"¡Excelente! Ya tienes la versión más reciente del SUA ({version_actual}).\n\nSe abrirá el programa.")
            ejecutar_sua(ruta_sua_exe)
            return

    # 3. Proceder con la actualización
    ventana = VentanaProgreso("Actualización SUA", f"Actualizando SUA de {version_actual} a {VERSION_A_INSTALAR}...")
    
    def proceso_actualizacion():
        try:
            if descargar_archivo(url_descarga, ruta_instalador, ventana):
                if instalar_actualizacion_silenciosa(ruta_instalador, ventana):
                    ventana.actualizar_estado("Actualización completada")
                    time.sleep(1)
                    ventana.cerrar()
                    mostrar_mensaje("¡Éxito!", f"El SUA se ha actualizado correctamente a la versión {VERSION_A_INSTALAR}.\n\nA continuación, se iniciará el programa.")
                    ejecutar_sua(ruta_sua_exe)
                else:
                    ventana.cerrar()
            else:
                ventana.cerrar()
        except Exception as e:
            ventana.cerrar()
            mostrar_mensaje("Error", f"Error durante la actualización:\n\nError: {e}")
    
    # Ejecutar en hilo separado
    threading.Thread(target=proceso_actualizacion, daemon=True).start()
    ventana.mostrar()

if __name__ == "__main__":
    main()