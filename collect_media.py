import os
import shutil
import csv

def collect_media(ruta_base):
    """
    Mueve todas las imágenes y videos de 'ruta_base' y sus subcarpetas
    a una carpeta llamada 'collect_media' en 'ruta_base',
    y genera un CSV dentro de esa misma carpeta con los detalles de cada archivo movido.
    """
    # ✅ Extensiones de medios soportadas
    extensiones_imagen = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff',
        '.heic', '.heif', '.webp'
    }
    extensiones_video = {
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'
    }
    extensiones_media = extensiones_imagen | extensiones_video

    # ✅ Crear carpeta de destino
    carpeta_destino = os.path.join(ruta_base, "00_collect_media")
    os.makedirs(carpeta_destino, exist_ok=True)

    # ✅ Ruta del CSV log
    ruta_csv = os.path.join(carpeta_destino, "00_collect_media_log.csv")
    archivos_movidos = []

    total_movidos = 0
    for carpeta, _, archivos in os.walk(ruta_base):
        # Evitar procesar la carpeta collect_media para no mover los archivos ya movidos
        if os.path.abspath(carpeta) == os.path.abspath(carpeta_destino):
            continue

        for archivo in archivos:
            ext = os.path.splitext(archivo)[1].lower()
            if ext in extensiones_media:
                ruta_origen = os.path.join(carpeta, archivo)
                destino = os.path.join(carpeta_destino, archivo)

                # ✅ Renombrar si el archivo ya existe en destino
                contador = 1
                while os.path.exists(destino):
                    nombre, extension = os.path.splitext(archivo)
                    destino = os.path.join(carpeta_destino, f"{nombre}_{contador}{extension}")
                    contador += 1

                try:
                    shutil.move(ruta_origen, destino)
                    total_movidos += 1
                    archivos_movidos.append([ruta_origen, destino])
                    print(f"📂 Movido: {ruta_origen} → {destino}")
                except Exception as e:
                    print(f"⚠️ Error moviendo {ruta_origen}: {e}")

    # ✅ Crear CSV con el log de los archivos movidos
    if archivos_movidos:
        with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Archivo Original", "Nueva Ubicación"])
            writer.writerows(archivos_movidos)
        print(f"\n📄 CSV generado en: {ruta_csv}")
    else:
        print("\n⚠️ No se movió ningún archivo, no se generó CSV.")

    print("\n✅ ¡Proceso completado!")
    print(f"📂 Total de archivos movidos: {total_movidos}")
    print(f"📁 Carpeta de destino: {carpeta_destino}")


if __name__ == "__main__":
    # 🔧 Cambia esta ruta a la carpeta que quieres escanear
    ruta_base = r"E:\ULTRA BACK UP"   # ← EJEMPLO
    collect_media(ruta_base)
