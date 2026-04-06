import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import re

# -----------------------
# CONFIG
# max path es el margen de longitud max de wind para los links. 
# -----------------------

MAX_PATH = 260  # margen seguro para Windows


# -----------------------
# Funciones de fecha
# -----------------------

def obtener_fecha_imagen_exif(ruta_imagen):
    try:
        img = Image.open(ruta_imagen)
        exif_data = img._getexif()
        if not exif_data:
            return None

        etiquetas_fecha = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag in etiquetas_fecha:
                try:
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                except:
                    continue
    except:
        return None

    return None


def fecha_desde_nombre(nombre_archivo):
    patrones = [
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',
        r'(\d{4})(\d{2})(\d{2})[_-]\d{6}',
    ]

    for patron in patrones:
        match = re.search(patron, nombre_archivo)
        if match:
            try:
                year, month, day = map(int, match.groups()[:3])
                return datetime(year, month, day)
            except:
                continue

    return None


def obtener_fecha_real(ruta_archivo, es_imagen=True):
    fechas = []

    if es_imagen:
        fecha_exif = obtener_fecha_imagen_exif(ruta_archivo)
        if fecha_exif:
            fechas.append(fecha_exif)

    fecha_nombre = fecha_desde_nombre(os.path.basename(ruta_archivo))
    if fecha_nombre:
        fechas.append(fecha_nombre)

    try:
        fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
        fechas.append(fecha_modificacion)
    except:
        return None

    return min(fechas) if fechas else None


# -----------------------
# Evitar sobrescritura
# -----------------------

def obtener_ruta_sin_conflicto(ruta_destino):
    if not os.path.exists(ruta_destino):
        return ruta_destino

    carpeta, nombre = os.path.split(ruta_destino)
    nombre_base, extension = os.path.splitext(nombre)

    contador = 1
    while True:
        nueva_ruta = os.path.join(carpeta, f"{nombre_base}_({contador}){extension}")
        if not os.path.exists(nueva_ruta):
            return nueva_ruta
        contador += 1


# -----------------------
# Excluir carpetas
# -----------------------

def esta_excluida(ruta, carpetas_excluidas):
    ruta = os.path.abspath(ruta)
    for excluida in carpetas_excluidas:
        if os.path.commonpath([ruta, excluida]) == excluida:
            return True
    return False


# -----------------------
# Función principal
# -----------------------

def ordenar_archivos_por_ano(ruta_origen, ruta_salida, carpetas_excluidas=None):

    if carpetas_excluidas is None:
        carpetas_excluidas = []

    carpetas_excluidas = [os.path.abspath(p) for p in carpetas_excluidas]

    extensiones_imagen = {'.jpg', '.jpeg', '.png', '.heic', '.heif', '.tif', '.tiff', '.bmp', '.gif', '.webp'}
    extensiones_video = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.mpeg', '.mpg'}
    todas_extensiones = extensiones_imagen | extensiones_video

    os.makedirs(ruta_salida, exist_ok=True)

    archivos = []

    print("🔍 Escaneando archivos...")

    for carpeta, subdirs, files in os.walk(ruta_origen):

        if esta_excluida(carpeta, carpetas_excluidas):
            continue

        for f in files:
            ruta_completa = os.path.join(carpeta, f)

            if len(ruta_completa) > MAX_PATH:
                print(f"⚠️ Ruta demasiado larga (omitida):\n{ruta_completa}\n")
                continue

            if os.path.splitext(f)[1].lower() in todas_extensiones:
                archivos.append(ruta_completa)

    total = len(archivos)
    print(f"📦 Total archivos a procesar: {total}\n")

    errores = 0
    omitidos = 0

    for i, ruta_archivo in enumerate(archivos, 1):

        try:
            if esta_excluida(ruta_archivo, carpetas_excluidas):
                omitidos += 1
                continue

            ext = os.path.splitext(ruta_archivo)[1].lower()
            es_imagen = ext in extensiones_imagen

            fecha = obtener_fecha_real(ruta_archivo, es_imagen)

            if not fecha:
                print(f"⚠️ Sin fecha válida: {ruta_archivo}")
                omitidos += 1
                continue

            carpeta_ano = os.path.join(ruta_salida, str(fecha.year))
            os.makedirs(carpeta_ano, exist_ok=True)

            nombre = os.path.basename(ruta_archivo)
            destino = os.path.join(carpeta_ano, nombre)

            if len(destino) > MAX_PATH:
                print(f"⚠️ Destino demasiado largo (omitido):\n{destino}\n")
                omitidos += 1
                continue

            destino = obtener_ruta_sin_conflicto(destino)

            shutil.copy2(ruta_archivo, destino)

            print(f"{i}/{total} → {destino}")

        except Exception as e:
            print(f"❌ Error con archivo:\n{ruta_archivo}\n{e}\n")
            errores += 1
            continue

    print("\n-----------------------")
    print("✅ Proceso completado")
    print(f"📦 Total procesados: {total}")
    print(f"⚠️ Omitidos: {omitidos}")
    print(f"❌ Errores: {errores}")
    print("-----------------------")


# -----------------------
# MAIN
# -----------------------

if __name__ == "__main__":

    ruta_origen = r"E:\Main Dokumente Back Up"
    ruta_salida = r"C:\Users\Ángel\Desktop\Fotos_new"

    carpetas_excluidas = [
        r"E:\Main Dokumente Back Up\DONE_01_Petita Ideas_Mai24",
        r"E:\Main Dokumente Back Up\Dokumente\01_Petita Ideas",
    ]

    ordenar_archivos_por_ano(ruta_origen, ruta_salida, carpetas_excluidas) 