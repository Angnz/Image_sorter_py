import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import re

# -----------------------
# Funciones de fecha
# -----------------------

def obtener_fecha_imagen_exif(ruta_imagen):
    """
    Intenta obtener la fecha de la imagen desde cualquier etiqueta EXIF válida.
    Retorna datetime o None si no se encuentra.
    """
    try:
        img = Image.open(ruta_imagen)
        exif_data = img._getexif()
        if not exif_data:
            return None

        etiquetas_fecha = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime', 'Aufnahmedatum']

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in etiquetas_fecha:
                try:
                    fecha = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    return fecha
                except Exception:
                    continue
    except Exception:
        return None

    return None

def fecha_desde_nombre(nombre_archivo):
    """
    Intenta extraer una fecha del nombre del archivo usando patrones comunes.
    """
    patrones = [
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',       # 2019-05-12, 20190512, 2019_05_12
        r'(\d{4})(\d{2})(\d{2})[_-]\d{6}',        # 20160629_115604
    ]
    for patron in patrones:
        match = re.search(patron, nombre_archivo)
        if match:
            try:
                year, month, day = map(int, match.groups()[:3])
                return datetime(year, month, day)
            except ValueError:
                continue
    return None

def obtener_fecha_real(ruta_archivo, es_imagen=True):
    """
    Obtiene la fecha final de un archivo:
    1. EXIF (si es imagen)
    2. Fecha en el nombre
    3. Fecha de modificación
    Luego devuelve la fecha más antigua entre las disponibles.
    """
    fechas = []

    if es_imagen:
        fecha_exif = obtener_fecha_imagen_exif(ruta_archivo)
        if fecha_exif:
            fechas.append(fecha_exif)

    fecha_nombre = fecha_desde_nombre(os.path.basename(ruta_archivo))
    if fecha_nombre:
        fechas.append(fecha_nombre)

    fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
    fechas.append(fecha_modificacion)

    # Filtrar None y tomar la fecha más antigua
    fechas_validas = [f for f in fechas if f is not None]
    if fechas_validas:
        return min(fechas_validas)
    else:
        return fecha_modificacion  # respaldo extremo

# -----------------------
# Funciones de conteo y listado
# -----------------------

def contar_archivos(ruta, extensiones):
    contador = 0
    for carpeta, _, archivos in os.walk(ruta):
        for archivo in archivos:
            if os.path.splitext(archivo)[1].lower() in extensiones:
                contador += 1
    return contador

def listar_archivos(ruta, extensiones, ruta_sorted):
    """Devuelve la lista de todos los archivos a procesar, ignorando 'sorted'."""
    archivos_lista = []
    for carpeta, _, archivos in os.walk(ruta):
        if os.path.commonpath([os.path.abspath(carpeta), os.path.abspath(ruta_sorted)]) == os.path.abspath(ruta_sorted):
            continue
        for archivo in archivos:
            if os.path.splitext(archivo)[1].lower() in extensiones:
                archivos_lista.append(os.path.join(carpeta, archivo))
    return archivos_lista

# -----------------------
# Función principal de orden
# -----------------------

def ordenar_archivos_por_fecha(ruta_origen):
    extensiones_imagen = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.tif', '.tiff', '.bmp', '.gif', '.webp'}
    extensiones_video = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'}
    todas_extensiones = extensiones_imagen | extensiones_video

    ruta_sorted = os.path.join(ruta_origen, "sorted")
    os.makedirs(ruta_sorted, exist_ok=True)

    archivos_a_procesar = listar_archivos(ruta_origen, todas_extensiones, ruta_sorted)
    total = len(archivos_a_procesar)

    for idx, ruta_archivo in enumerate(archivos_a_procesar, start=1):
        ext = os.path.splitext(ruta_archivo)[1].lower()
        es_imagen = ext in extensiones_imagen
        fecha = obtener_fecha_real(ruta_archivo, es_imagen=es_imagen)

        carpeta_ano = os.path.join(ruta_sorted, f"{fecha.year}")
        carpeta_destino = os.path.join(carpeta_ano, f"{fecha.year}_{fecha.month:02d}")
        os.makedirs(carpeta_destino, exist_ok=True)

        shutil.copy2(ruta_archivo, carpeta_destino)
        print(f"{idx}/{total} Copiado: {ruta_archivo} → {carpeta_destino}")

    return todas_extensiones, ruta_sorted

# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":
    ruta = r"E:\HDD1 Backup\Doks back uo\01_Petita Ideas"  # 🔧 Cambia por tu carpeta

    extensiones_imagen = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.tif', '.tiff', '.bmp', '.gif', '.webp'}
    extensiones_video = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'}
    todas_extensiones = extensiones_imagen | extensiones_video

    total_origen = contar_archivos(ruta, todas_extensiones)
    _, ruta_sorted = ordenar_archivos_por_fecha(ruta)
    total_sorted = contar_archivos(ruta_sorted, todas_extensiones)

    print("\n✅ ¡Proceso completado!")
    print(f"📂 Total archivos en carpeta original: {total_origen}")
    print(f"📂 Total archivos en carpeta 'sorted': {total_sorted}")
