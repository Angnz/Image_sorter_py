import os
from datetime import datetime
import time

def renombrar_lote(carpeta, prefijo="IMG"):
    archivos = sorted([f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))])
    for idx, archivo in enumerate(archivos, start=1):
        ext = os.path.splitext(archivo)[1].lower()
        nuevo_nombre = f"{prefijo}_{idx:03d}{ext}"
        os.rename(os.path.join(carpeta, archivo), os.path.join(carpeta, nuevo_nombre))
        print(f"{archivo} → {nuevo_nombre}")
    print("\n✅ Renombrado completado!")

def cambiar_fecha_lote(carpeta, fecha_str):
    """
    Cambia la fecha de modificación de todos los archivos de la carpeta.
    fecha_str: "YYYY-MM-DD HH:MM:SS"
    """
    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(fecha_obj.timetuple())

    archivos = [f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)
        os.utime(ruta, (timestamp, timestamp))
        print(f"Fecha cambiada: {archivo} → {fecha_str}")
    print("\n✅ Fecha modificada en todos los archivos!")

# -----------------------------
# Menú principal
# -----------------------------

if __name__ == "__main__":
    print("=== Herramienta de lote para imágenes/videos ===")
    print("1) Renombrar lote de archivos")
    print("2) Cambiar fecha de modificación de los archivos")
    opcion = input("Selecciona opción (1 o 2): ").strip()

    carpeta = input("Ruta de la carpeta: ").strip()
    if not os.path.isdir(carpeta):
        print("❌ Carpeta no válida.")
        exit()

    if opcion == "1":
        prefijo = input("Prefijo para los archivos (ej: IMG): ").strip()
        renombrar_lote(carpeta, prefijo=prefijo)

    elif opcion == "2":
        fecha_str = input("Nueva fecha (YYYY-MM-DD HH:MM:SS): ").strip()
        cambiar_fecha_lote(carpeta, fecha_str)

    else:
        print("❌ Opción no válida.")
